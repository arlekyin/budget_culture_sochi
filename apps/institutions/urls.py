from django.urls import path
from . import views

urlpatterns = [
    path('', views.InstitutionListView.as_view(), name='institution_list'),
    path('<int:pk>/', views.InstitutionDetailView.as_view(), name='institution_detail'),
]
