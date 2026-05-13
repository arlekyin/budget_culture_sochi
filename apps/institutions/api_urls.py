from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.InstitutionListAPI.as_view(), name='api_institution_list'),
    path('<int:pk>/', api_views.InstitutionDetailAPI.as_view(), name='api_institution_detail'),
]
