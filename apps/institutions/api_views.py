"""
API views для учреждений.
"""
from decimal import Decimal

from django.db.models import Sum
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Institution, BudgetLimit
from .serializers import InstitutionSerializer, InstitutionListSerializer
from apps.budget_requests.models import BudgetRequest, RequestStatus
from apps.monitoring.models import FactPayment


class InstitutionListAPI(ListAPIView):
    """GET /api/institutions/ — список активных учреждений."""

    serializer_class = InstitutionListSerializer
    permission_classes = [IsAuthenticated]
    queryset = Institution.objects.filter(is_active=True).order_by('short_name')


class InstitutionDetailAPI(RetrieveAPIView):
    """GET /api/institutions/:id/ — детальная карточка учреждения."""

    serializer_class = InstitutionSerializer
    permission_classes = [IsAuthenticated]
    queryset = Institution.objects.filter(is_active=True).prefetch_related('limits')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        # Добавляем последние 5 заявок
        recent_requests = BudgetRequest.objects.filter(
            institution=instance
        ).order_by('-created_at')[:5]

        data['recent_requests'] = [
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
            for r in recent_requests
        ]

        # Текущий год: лимит, факт, остаток
        year = 2026
        limit_obj = BudgetLimit.objects.filter(institution=instance, year=year).first()
        limit = limit_obj.total_limit if limit_obj else Decimal('0')
        fact = FactPayment.objects.filter(
            institution=instance, year=year
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        data['current_year_stats'] = {
            'year': year,
            'limit': str(limit),
            'fact': str(fact),
            'balance': str(limit - fact),
            'pct': int(fact / limit * 100) if limit else 0,
        }

        return Response(data)
