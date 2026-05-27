"""
API views для аутентификации и дашборда.
"""
import json
from decimal import Decimal

from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status

from apps.accounts.models import UserRole
from apps.accounts.utils import get_role
from apps.budget_requests.models import BudgetRequest, RequestStatus
from apps.institutions.models import Institution, BudgetLimit
from apps.monitoring.models import FactPayment, Reservation
from apps.classifiers.models import KOSGU


class LoginAPI(APIView):
    """POST /api/auth/login/ — авторизация по логину и паролю."""

    permission_classes = [AllowAny]

    def post(self, request) -> Response:
        data = request.data
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            return Response(
                {'detail': 'Необходимо указать логин и пароль.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {'detail': 'Неверный логин или пароль.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        login(request, user)
        return Response(_serialize_user(user))


class LogoutAPI(APIView):
    """POST /api/auth/logout/ — завершение сессии."""

    permission_classes = [IsAuthenticated]

    def post(self, request) -> Response:
        logout(request)
        return Response({'detail': 'Выход выполнен.'})


@method_decorator(ensure_csrf_cookie, name='dispatch')
class MeAPI(APIView):
    """GET /api/auth/me/ — текущий пользователь и его роль."""

    permission_classes = [IsAuthenticated]

    def get(self, request) -> Response:
        return Response(_serialize_user(request.user))


class DashboardAPI(APIView):
    """GET /api/dashboard/ — данные дашборда в зависимости от роли."""

    permission_classes = [IsAuthenticated]

    def get(self, request) -> Response:
        user = request.user
        role = get_role(user)
        year = int(request.GET.get('year', 2026))

        if role == UserRole.DIRECTOR:
            try:
                profile = user.profile
            except Exception:
                return Response({'detail': 'Профиль не найден.'}, status=404)
            return Response(_director_dashboard(profile, year))
        elif role == UserRole.ACCOUNTANT:
            return Response(_accountant_dashboard(year))
        else:
            # HEAD or ADMIN (including superuser)
            return Response(_head_dashboard(year))


# ---------------------------------------------------------------------------
# Вспомогательные функции
# ---------------------------------------------------------------------------

def _serialize_user(user) -> dict:
    """Сериализует пользователя и его профиль."""
    if user.is_superuser:
        return {
            'id': user.id,
            'username': user.username,
            'firstName': user.first_name,
            'lastName': user.last_name,
            'role': UserRole.ADMIN,
            'roleDisplay': 'Администратор системы',
            'institution': None,
        }
    try:
        profile = user.profile
        institution = None
        if profile.institution:
            institution = {
                'id': profile.institution.id,
                'name': profile.institution.short_name,
            }
        return {
            'id': user.id,
            'username': user.username,
            'firstName': user.first_name,
            'lastName': user.last_name,
            'role': profile.role,
            'roleDisplay': profile.get_role_display(),
            'institution': institution,
        }
    except Exception:
        return {
            'id': user.id,
            'username': user.username,
            'firstName': user.first_name,
            'lastName': user.last_name,
            'role': None,
            'roleDisplay': '',
            'institution': None,
        }


def _director_dashboard(profile, year: int) -> dict:
    """Данные дашборда для директора учреждения."""
    institution = profile.institution
    if not institution:
        return {'error': 'Учреждение не привязано к профилю.'}

    limit_obj = BudgetLimit.objects.filter(institution=institution, year=year).first()
    limit = limit_obj.total_limit if limit_obj else Decimal('0')

    approved_qs = BudgetRequest.objects.filter(
        institution=institution,
        period_year=year,
        status__in=[RequestStatus.APPROVED, RequestStatus.INCLUDED],
    )
    fact_total = FactPayment.objects.filter(
        institution=institution, year=year
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    reserved_total = Reservation.objects.filter(
        institution=institution, year=year, status='active'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    approved_total = approved_qs.aggregate(
        total=Sum('approved_amount')
    )['total'] or Decimal('0')

    free = limit - fact_total - reserved_total
    pct_used = int(fact_total / limit * 100) if limit else 0

    recent = BudgetRequest.objects.filter(
        institution=institution
    ).select_related('institution').order_by('-created_at')[:5]

    recent_requests = [
        {
            'id': r.id,
            'period_year': r.period_year,
            'period_type': r.period_type,
            'status': r.status,
            'status_display': r.get_status_display(),
            'total_amount': str(r.total_amount),
            'approved_amount': str(r.approved_amount) if r.approved_amount else None,
            'created_at': r.created_at.isoformat(),
        }
        for r in recent
    ]

    return {
        'role': UserRole.DIRECTOR,
        'institution': {
            'id': institution.id,
            'name': institution.short_name,
            'full_name': institution.name,
        },
        'limit': str(limit),
        'fact_total': str(fact_total),
        'reserved_total': str(reserved_total),
        'approved_total': str(approved_total),
        'free': str(free),
        'pct_used': pct_used,
        'year': year,
        'recent_requests': recent_requests,
    }


def _accountant_dashboard(year: int) -> dict:
    """Данные дашборда для бухгалтера ЦБ."""
    pending = BudgetRequest.objects.filter(status=RequestStatus.SUBMITTED).count()

    stats = BudgetRequest.objects.filter(period_year=year).aggregate(
        draft=Count('id', filter=Q(status=RequestStatus.DRAFT)),
        submitted=Count('id', filter=Q(status=RequestStatus.SUBMITTED)),
        approved=Count('id', filter=Q(status=RequestStatus.APPROVED)),
        included=Count('id', filter=Q(status=RequestStatus.INCLUDED)),
        total_approved=Sum(
            'approved_amount',
            filter=Q(status__in=[RequestStatus.APPROVED, RequestStatus.INCLUDED])
        ),
    )

    submitted_requests = BudgetRequest.objects.filter(
        status=RequestStatus.SUBMITTED
    ).select_related('institution').order_by('-submitted_at')[:20]

    incoming = [
        {
            'id': r.id,
            'institution_name': r.institution.short_name,
            'period_year': r.period_year,
            'period_type': r.get_period_type_display(),
            'total_amount': str(r.total_amount),
            'submitted_at': r.submitted_at.isoformat() if r.submitted_at else None,
            'deadline': r.deadline.isoformat() if r.deadline else None,
        }
        for r in submitted_requests
    ]

    return {
        'role': UserRole.ACCOUNTANT,
        'year': year,
        'pending_requests': pending,
        'stats': {
            'draft': stats['draft'] or 0,
            'submitted': stats['submitted'] or 0,
            'approved': (stats['approved'] or 0) + (stats['included'] or 0),
            'total_approved_amount': str(stats['total_approved'] or Decimal('0')),
        },
        'incoming_requests': incoming,
    }


def _head_dashboard(year: int) -> dict:
    """Данные дашборда для руководителя/администратора."""
    institutions = Institution.objects.filter(is_active=True)

    total_limit = BudgetLimit.objects.filter(year=year).aggregate(
        total=Sum('total_limit')
    )['total'] or Decimal('0')

    total_fact = FactPayment.objects.filter(year=year).aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')

    pct_overall = int(total_fact / total_limit * 100) if total_limit else 0

    institution_stats = []
    for inst in institutions:
        limit_obj = BudgetLimit.objects.filter(institution=inst, year=year).first()
        limit = limit_obj.total_limit if limit_obj else Decimal('0')

        fact = FactPayment.objects.filter(
            institution=inst, year=year
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        pct = int(fact / limit * 100) if limit else 0

        institution_stats.append({
            'id': inst.id,
            'name': inst.short_name,
            'limit': str(limit),
            'fact': str(fact),
            'pct': pct,
        })

    # Разбивка по КОСГУ (топ 8)
    kosgu_payments = FactPayment.objects.filter(year=year).values(
        'kosgu__code', 'kosgu__name'
    ).annotate(total=Sum('amount')).order_by('-total')[:8]

    kosgu_breakdown = [
        {
            'code': item['kosgu__code'],
            'name': item['kosgu__name'],
            'total': str(item['total']),
        }
        for item in kosgu_payments
    ]

    return {
        'role': 'head',
        'year': year,
        'total_limit': str(total_limit),
        'total_fact': str(total_fact),
        'pct_overall': pct_overall,
        'institution_stats': institution_stats,
        'kosgu_breakdown': kosgu_breakdown,
    }
