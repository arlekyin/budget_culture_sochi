from django.urls import path
from . import api_views

urlpatterns = [
    path('fact-payments/', api_views.FactPaymentListCreateAPI.as_view(), name='api_fact_payments'),
    path('reservations/', api_views.ReservationListCreateAPI.as_view(), name='api_reservations'),
]
