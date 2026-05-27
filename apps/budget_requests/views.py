from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q

from apps.accounts.models import UserRole
from .models import BudgetRequest, RequestLine, RequestStatus, RequestLineLog
from .forms import AdminBudgetRequestForm, BudgetRequestForm, RequestLineForm, ReviewForm


def _role(request):
    if request.user.is_superuser:
        return UserRole.ADMIN
    try:
        return request.user.profile.role
    except Exception:
        return None


def _is_admin(request) -> bool:
    return _role(request) == UserRole.ADMIN


@login_required
def request_list(request):
    """Список заявок — фильтруется по роли пользователя."""
    role = _role(request)
    qs = BudgetRequest.objects.select_related('institution', 'created_by')

    if role == UserRole.DIRECTOR:
        institution = request.user.profile.institution
        qs = qs.filter(institution=institution)
    # Бухгалтер и выше видят все

    # Фильтрация по статусу
    status_filter = request.GET.get('status')
    if status_filter:
        qs = qs.filter(status=status_filter)

    year_filter = request.GET.get('year')
    if year_filter:
        qs = qs.filter(period_year=year_filter)

    return render(request, 'budget_requests/list.html', {
        'requests': qs.order_by('-created_at'),
        'status_choices': RequestStatus.choices,
        'current_status': status_filter,
        'current_year': year_filter,
    })


@login_required
def request_create(request):
    """Создание новой бюджетной заявки (директор учреждения или администратор)."""
    role = _role(request)
    is_admin = role == UserRole.ADMIN

    if role not in (UserRole.DIRECTOR, UserRole.ADMIN):
        messages.error(request, 'Создавать заявки могут только директора учреждений или администратор.')
        return redirect('request_list')

    form_class = AdminBudgetRequestForm if is_admin else BudgetRequestForm

    if not is_admin:
        institution = request.user.profile.institution
        if not institution:
            messages.error(request, 'Ваш профиль не привязан к учреждению.')
            return redirect('dashboard')
    else:
        institution = None

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            budget_request = form.save(commit=False)
            budget_request.institution = form.cleaned_data['institution'] if is_admin else institution
            budget_request.created_by = request.user
            budget_request.status = RequestStatus.DRAFT
            budget_request.save()
            messages.success(request, 'Заявка создана. Теперь добавьте строки расходов.')
            return redirect('request_detail', pk=budget_request.pk)
    else:
        form = form_class()

    return render(request, 'budget_requests/create.html', {'form': form, 'institution': institution})


@login_required
def request_detail(request, pk: int):
    """Просмотр и редактирование заявки."""
    budget_request = get_object_or_404(BudgetRequest, pk=pk)
    role = _role(request)

    # Директор видит только свои заявки; администратор видит все
    if role == UserRole.DIRECTOR:
        if budget_request.institution != request.user.profile.institution:
            messages.error(request, 'Доступ запрещён.')
            return redirect('request_list')

    lines = budget_request.lines.select_related('kosgu', 'kvr').all()
    can_edit = (
        budget_request.status in (RequestStatus.DRAFT, RequestStatus.RETURNED)
        and role in (UserRole.DIRECTOR, UserRole.ADMIN)
    )
    can_submit = can_edit and budget_request.lines.exists()
    can_review = (
        role in (UserRole.ACCOUNTANT, UserRole.ADMIN)
        and budget_request.status == RequestStatus.SUBMITTED
    )

    line_form = RequestLineForm() if can_edit else None
    review_form = ReviewForm() if can_review else None

    return render(request, 'budget_requests/detail.html', {
        'request': budget_request,
        'lines': lines,
        'can_edit': can_edit,
        'can_submit': can_submit,
        'can_review': can_review,
        'line_form': line_form,
        'review_form': review_form,
        'limit_ok': budget_request.check_limit(),
    })


@login_required
def request_line_add(request, pk: int):
    """Добавление строки расхода в заявку."""
    budget_request = get_object_or_404(BudgetRequest, pk=pk)
    role = _role(request)

    if not _is_admin(request) and (
        role != UserRole.DIRECTOR
        or budget_request.institution != request.user.profile.institution
    ):
        messages.error(request, 'Доступ запрещён.')
        return redirect('request_list')

    if budget_request.status not in (RequestStatus.DRAFT, RequestStatus.RETURNED):
        messages.error(request, 'Нельзя редактировать заявку в текущем статусе.')
        return redirect('request_detail', pk=pk)

    if request.method == 'POST':
        form = RequestLineForm(request.POST, request.FILES)
        if form.is_valid():
            line = form.save(commit=False)
            line.request = budget_request
            line.save()
            messages.success(request, 'Строка добавлена.')
        else:
            messages.error(request, 'Ошибка в форме. Проверьте введённые данные.')

    return redirect('request_detail', pk=pk)


@login_required
def request_line_delete(request, pk: int, line_pk: int):
    """Удаление строки расхода."""
    budget_request = get_object_or_404(BudgetRequest, pk=pk)
    line = get_object_or_404(RequestLine, pk=line_pk, request=budget_request)
    role = _role(request)

    if not _is_admin(request) and (
        role != UserRole.DIRECTOR
        or budget_request.institution != request.user.profile.institution
    ):
        messages.error(request, 'Доступ запрещён.')
        return redirect('request_list')

    if budget_request.status not in (RequestStatus.DRAFT, RequestStatus.RETURNED):
        messages.error(request, 'Нельзя редактировать заявку в текущем статусе.')
        return redirect('request_detail', pk=pk)

    line.delete()
    messages.success(request, 'Строка удалена.')
    return redirect('request_detail', pk=pk)


@login_required
def request_submit(request, pk: int):
    """Отправка заявки на проверку в ЦБ."""
    budget_request = get_object_or_404(BudgetRequest, pk=pk)
    role = _role(request)

    if not _is_admin(request) and (
        role != UserRole.DIRECTOR
        or budget_request.institution != request.user.profile.institution
    ):
        messages.error(request, 'Доступ запрещён.')
        return redirect('request_list')

    if budget_request.status not in (RequestStatus.DRAFT, RequestStatus.RETURNED):
        messages.error(request, 'Заявка уже отправлена или в неподходящем статусе.')
        return redirect('request_detail', pk=pk)

    if not budget_request.lines.exists():
        messages.error(request, 'Нельзя отправить пустую заявку. Добавьте строки расходов.')
        return redirect('request_detail', pk=pk)

    if not budget_request.check_limit():
        messages.warning(
            request,
            f'Внимание: сумма заявки ({budget_request.total_amount} руб.) '
            f'превышает установленный лимит. Заявка отправлена, но бухгалтер будет уведомлён.'
        )

    budget_request.status = RequestStatus.SUBMITTED
    budget_request.submitted_at = timezone.now()
    budget_request.save(update_fields=['status', 'submitted_at'])
    messages.success(request, 'Заявка отправлена на проверку в Централизованную бухгалтерию.')
    return redirect('request_detail', pk=pk)


@login_required
def request_review(request, pk: int):
    """Обработка заявки бухгалтером ЦБ."""
    budget_request = get_object_or_404(BudgetRequest, pk=pk)
    role = _role(request)

    if role not in (UserRole.ACCOUNTANT, UserRole.ADMIN):
        messages.error(request, 'Только бухгалтер ЦБ или администратор может проверять заявки.')
        return redirect('request_list')

    if budget_request.status != RequestStatus.SUBMITTED:
        messages.error(request, 'Заявка не находится на проверке.')
        return redirect('request_detail', pk=pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            comment = form.cleaned_data.get('comment', '')
            approved_amount = form.cleaned_data.get('approved_amount')

            budget_request.reviewed_by = request.user
            budget_request.reviewed_at = timezone.now()
            budget_request.comment = comment

            if action == 'approve':
                budget_request.status = RequestStatus.APPROVED
                budget_request.approved_amount = approved_amount or budget_request.total_amount
                messages.success(request, 'Заявка согласована.')
            elif action == 'return':
                if not comment:
                    messages.error(request, 'При возврате необходимо указать причину.')
                    return redirect('request_detail', pk=pk)
                budget_request.status = RequestStatus.RETURNED
                messages.info(request, 'Заявка возвращена на доработку.')
            elif action == 'reject':
                if not comment:
                    messages.error(request, 'При отклонении необходимо указать причину.')
                    return redirect('request_detail', pk=pk)
                budget_request.status = RequestStatus.REJECTED
                messages.warning(request, 'Заявка отклонена.')

            budget_request.save()
        else:
            messages.error(request, 'Ошибка формы.')

    return redirect('request_detail', pk=pk)
