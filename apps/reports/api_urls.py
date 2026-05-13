from django.urls import path
from . import api_views

urlpatterns = [
    path('consolidated/', api_views.ConsolidatedReportAPI.as_view(), name='api_consolidated_report'),
    path('export/excel/', api_views.ExportExcelAPI.as_view(), name='api_export_excel'),
]
