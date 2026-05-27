from django import forms
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy

from .models import UserProfile, UserRole


class UserWithProfileForm(UserCreationForm):
    """Форма регистрации пользователя с указанием роли и учреждения."""

    first_name = forms.CharField(max_length=150, required=False, label='Имя')
    last_name = forms.CharField(max_length=150, required=False, label='Фамилия')
    role = forms.ChoiceField(
        choices=UserRole.choices,
        label='Роль',
        initial=UserRole.DIRECTOR,
    )
    institution = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label='Учреждение (только для директора)',
        empty_label='— не привязано —',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.institutions.models import Institution
        self.fields['institution'].queryset = Institution.objects.filter(
            is_active=True
        ).order_by('short_name')
        # Порядок полей
        field_order = [
            'username', 'first_name', 'last_name',
            'role', 'institution',
            'password1', 'password2',
        ]
        self.fields = {k: self.fields[k] for k in field_order}

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2')


class RegisterView(CreateView):
    """Регистрация нового пользователя (только через администратора)."""

    form_class = UserWithProfileForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('user_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        role = _get_role(request.user)
        if role != UserRole.ADMIN:
            messages.error(request, 'Создавать пользователей может только администратор.')
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save(commit=False)
        user.first_name = form.cleaned_data.get('first_name', '')
        user.last_name = form.cleaned_data.get('last_name', '')
        user.save()

        role = form.cleaned_data['role']
        institution = form.cleaned_data.get('institution')
        # Сигнал уже мог создать профиль, обновляем или создаём
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = role
        if role == UserRole.DIRECTOR:
            profile.institution = institution
        else:
            profile.institution = None
        profile.save()

        messages.success(self.request, f'Пользователь «{user.username}» создан с ролью «{profile.get_role_display()}».')
        return redirect(self.success_url)


@login_required
def user_list(request):
    """Список пользователей (только для администратора)."""
    role = _get_role(request.user)
    if role != UserRole.ADMIN:
        messages.error(request, 'Доступ только для администратора.')
        return redirect('dashboard')

    users = User.objects.select_related('profile', 'profile__institution').order_by('username')
    return render(request, 'accounts/user_list.html', {'users': users})


@login_required
def user_edit(request, pk: int):
    """Редактирование роли и учреждения пользователя (только для администратора)."""
    role = _get_role(request.user)
    if role != UserRole.ADMIN:
        messages.error(request, 'Доступ только для администратора.')
        return redirect('dashboard')

    target_user = get_object_or_404(User, pk=pk)
    profile, _ = UserProfile.objects.get_or_create(user=target_user)

    if request.method == 'POST':
        new_role = request.POST.get('role')
        institution_id = request.POST.get('institution')

        if new_role not in dict(UserRole.choices):
            messages.error(request, 'Недопустимая роль.')
        else:
            profile.role = new_role
            if new_role == UserRole.DIRECTOR and institution_id:
                from apps.institutions.models import Institution
                try:
                    profile.institution = Institution.objects.get(pk=institution_id)
                except Institution.DoesNotExist:
                    profile.institution = None
            else:
                profile.institution = None
            profile.save()
            messages.success(request, f'Роль пользователя «{target_user.username}» обновлена.')
            return redirect('user_list')

    from apps.institutions.models import Institution
    institutions = Institution.objects.filter(is_active=True).order_by('short_name')
    return render(request, 'accounts/user_edit.html', {
        'target_user': target_user,
        'profile': profile,
        'roles': UserRole.choices,
        'institutions': institutions,
    })


@login_required
def user_delete(request, pk: int):
    """Удаление пользователя (только для администратора)."""
    role = _get_role(request.user)
    if role != UserRole.ADMIN:
        messages.error(request, 'Доступ только для администратора.')
        return redirect('dashboard')

    target_user = get_object_or_404(User, pk=pk)
    if target_user == request.user:
        messages.error(request, 'Нельзя удалить самого себя.')
        return redirect('user_list')

    if request.method == 'POST':
        username = target_user.username
        target_user.delete()
        messages.success(request, f'Пользователь «{username}» удалён.')
        return redirect('user_list')

    return render(request, 'accounts/user_confirm_delete.html', {'target_user': target_user})


def _get_role(user) -> str | None:
    if user.is_superuser:
        return UserRole.ADMIN
    try:
        return user.profile.role
    except Exception:
        return None
