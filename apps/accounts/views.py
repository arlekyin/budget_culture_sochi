from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.views.generic import CreateView
from django.urls import reverse_lazy


class RegisterView(CreateView):
    """Регистрация нового пользователя (только через администратора)."""

    form_class = UserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        # Регистрация открыта только для суперпользователя
        if not request.user.is_superuser:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)
