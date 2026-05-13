from django.urls import path
from . import views

urlpatterns = [
    path('', views.request_list, name='request_list'),
    path('create/', views.request_create, name='request_create'),
    path('<int:pk>/', views.request_detail, name='request_detail'),
    path('<int:pk>/submit/', views.request_submit, name='request_submit'),
    path('<int:pk>/review/', views.request_review, name='request_review'),
    path('<int:pk>/lines/add/', views.request_line_add, name='request_line_add'),
    path('<int:pk>/lines/<int:line_pk>/delete/', views.request_line_delete, name='request_line_delete'),
]
