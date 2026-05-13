from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, DetailView
from django.urls import reverse_lazy
from django.db.models import Sum, Q

from apps.institutions.models import Institution, BudgetLimit
from apps.budget_requests.models import BudgetRequest, RequestStatus
from apps.monitoring.models import FactPayment, Reservation
from apps.accounts.models import UserRole


def _get_role(request):
    """Вспомогательная функция: возвращает роль текущего пользователя."""
    try:
        return request.user.profile.role
    except Exception:
        return None


@login_required
def dashboard(request):
    """
    Главный дашборд — показывает разный контент в зависимости от роли.
    """
    role = _get_role(request)
    year = 2026  # Текущий плановый год (можно вынести в настройки)

    if role == UserRole.DIRECTOR:
        # Директор видит только своё учреждение
        institution = request.user.profile.institution
        if not institution:
            return render(request, 'dashboard/no_institution.html')

        limit_obj = BudgetLimit.objects.filter(institution=institution, year=year).first()
        limit = limit_obj.total_limit if limit_obj else Decimal('0')

        fact_total = FactPayment.objects.filter(
            institution=institution, year=year
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        reserved_total = Reservation.objects.filter(
            institution=institution, year=year,
            status=Reservation.ReservationStatus.ACTIVE
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        free = limit - fact_total - reserved_total
        pct_used = int(fact_total / limit * 100) if limit else 0

        requests_qs = BudgetRequest.objects.filter(institution=institution).order_by('-created_at')[:5]

        return render(request, 'dashboard/director.html', {
            'institution': institution,
            'year': year,
            'limit': limit,
            'fact_total': fact_total,
            'reserved_total': reserved_total,
            'free': free,
            'pct_used': pct_used,
            'recent_requests': requests_qs,
        })

    elif role == UserRole.ACCOUNTANT:
        # Бухгалтер видит входящие заявки
        pending = BudgetRequest.objects.filter(
            status=RequestStatus.SUBMITTED
        ).select_related('institution').order_by('-submitted_at')

        stats = {
            'draft': BudgetRequest.objects.filter(status=RequestStatus.DRAFT).count(),
            'submitted': BudgetRequest.objects.filter(status=RequestStatus.SUBMITTED).count(),
            'approved': BudgetRequest.objects.filter(status=RequestStatus.APPROVED, period_year=year).count(),
            'total_approved_amount': BudgetRequest.objects.filter(
                status=RequestStatus.APPROVED, period_year=year
            ).aggregate(total=Sum('approved_amount'))['total'] or Decimal('0'),
        }

        return render(request, 'dashboard/accountant.html', {
            'pending_requests': pending,
            'stats': stats,
            'year': year,
        })

    elif role in (UserRole.HEAD, UserRole.ADMIN):
        # Руководитель и администратор видят общую аналитику
        institutions = Institution.objects.filter(is_active=True)
        total_limit = BudgetLimit.objects.filter(year=year).aggregate(
            total=Sum('total_limit')
        )['total'] or Decimal('0')
        total_fact = FactPayment.objects.filter(year=year).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        pct_overall = int(total_fact / total_limit * 100) if total_limit else 0

        # Данные для круговой диаграммы: факт по КОСГУ
        kosgu_breakdown = FactPayment.objects.filter(year=year).values(
            'kosgu__code', 'kosgu__name'
        ).annotate(total=Sum('amount')).order_by('-total')[:8]

        # Исполнение по учреждениям
        institution_stats = []
        for inst in institutions:
            lim = BudgetLimit.objects.filter(institution=inst, year=year).first()
            fact = FactPayment.objects.filter(institution=inst, year=year).aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0')
            limit_val = lim.total_limit if lim else Decimal('0')
            pct = int(fact / limit_val * 100) if limit_val else 0
            institution_stats.append({
                'institution': inst,
                'limit': limit_val,
                'fact': fact,
                'pct': pct,
            })

        return render(request, 'dashboard/head.html', {
            'year': year,
            'total_limit': total_limit,
            'total_fact': total_fact,
            'pct_overall': pct_overall,
            'kosgu_breakdown': list(kosgu_breakdown),
            'institution_stats': institution_stats,
        })

    return render(request, 'dashboard/director.html')


@login_required
def fact_payment_create(request):
    """Добавление кассового расхода бухгалтером."""
    from apps.monitoring.forms import FactPaymentForm
    if request.method == 'POST':
        form = FactPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.added_by = request.user
            payment.save()
            return redirect('dashboard')
    else:
        form = FactPaymentForm()
    return render(request, 'monitoring/fact_payment_form.html', {'form': form})


@login_required
def reservation_create(request):
    """Создание бронирования (заключение договора)."""
    from apps.monitoring.forms import ReservationForm
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.created_by = request.user
            reservation.save()
            return redirect('dashboard')
    else:
        form = ReservationForm()
    return render(request, 'monitoring/reservation_form.html', {'form': form})
