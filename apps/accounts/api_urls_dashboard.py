from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.DashboardAPI.as_view(), name='api_dashboard'),
]
