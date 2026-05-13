"""
API views для мониторинга: кассовые расходы и бронирования.
"""
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import UserRole
from .models import FactPayment, Reservation
from .serializers import FactPaymentSerializer, ReservationSerializer


class FactPaymentListCreateAPI(generics.ListCreateAPIView):
    """
    GET  /api/monitoring/fact-payments/ — список кассовых расходов.
    POST /api/monitoring/fact-payments/ — создать кассовый расход.
    """

    serializer_class = FactPaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            profile = user.profile
            role = profile.role
        except Exception:
            return FactPayment.objects.none()

        qs = FactPayment.objects.select_related('institution', 'kosgu', 'added_by')

        # Директор видит только своё учреждение
        if role == UserRole.DIRECTOR and profile.institution:
            qs = qs.filter(institution=profile.institution)

        # Фильтры по году и учреждению
        year = self.request.query_params.get('year')
        if year:
            qs = qs.filter(year=year)

        institution_id = self.request.query_params.get('institution')
        if institution_id:
            qs = qs.filter(institution_id=institution_id)

        return qs.order_by('-payment_date')


class ReservationListCreateAPI(generics.ListCreateAPIView):
    """
    GET  /api/monitoring/reservations/ — список бронирований.
    POST /api/monitoring/reservations/ — создать бронирование.
    """

    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            profile = user.profile
            role = profile.role
        except Exception:
            return Reservation.objects.none()

        qs = Reservation.objects.select_related('institution', 'kosgu', 'created_by')

        if role == UserRole.DIRECTOR and profile.institution:
            qs = qs.filter(institution=profile.institution)

        year = self.request.query_params.get('year')
        if year:
            qs = qs.filter(year=year)

        institution_id = self.request.query_params.get('institution')
        if institution_id:
            qs = qs.filter(institution_id=institution_id)

        return qs.order_by('-contract_date')
