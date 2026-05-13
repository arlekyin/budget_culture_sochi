from django.urls import path
from . import api_views

urlpatterns = [
    # Список и создание заявок
    path('requests/', api_views.BudgetRequestListAPI.as_view(), name='api_request_list'),
    path('requests/create/', api_views.BudgetRequestCreateAPI.as_view(), name='api_request_create'),
    # Детальная заявка и действия
    path('requests/<int:pk>/', api_views.BudgetRequestDetailAPI.as_view(), name='api_request_detail'),
    path('requests/<int:pk>/submit/', api_views.BudgetRequestSubmitAPI.as_view(), name='api_request_submit'),
    path('requests/<int:pk>/review/', api_views.BudgetRequestReviewAPI.as_view(), name='api_request_review'),
    # Строки заявки
    path('requests/<int:pk>/lines/', api_views.RequestLineAddAPI.as_view(), name='api_line_add'),
    path('requests/<int:pk>/lines/<int:line_id>/', api_views.RequestLineDeleteAPI.as_view(), name='api_line_delete'),
    path('requests/<int:pk>/logs/', api_views.RequestLineLogsAPI.as_view(), name='api_line_logs'),
    # Классификаторы
    path('classifiers/kosgu/', api_views.KOSGUListAPI.as_view(), name='api_kosgu_list'),
    path('classifiers/kvr/', api_views.KVRListAPI.as_view(), name='api_kvr_list'),
]
