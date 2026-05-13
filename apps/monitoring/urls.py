from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('fact-payments/add/', views.fact_payment_create, name='fact_payment_create'),
    path('reservations/add/', views.reservation_create, name='reservation_create'),
]
