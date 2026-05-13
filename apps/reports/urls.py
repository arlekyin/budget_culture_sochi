from django.urls import path
from . import views

urlpatterns = [
    path('consolidated/', views.consolidated_report, name='consolidated_report'),
    path('export/excel/', views.export_excel, name='export_excel'),
]
