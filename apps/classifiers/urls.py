from django.urls import path
from . import views

urlpatterns = [
    path('kosgu/', views.KOSGUListView.as_view(), name='kosgu_list'),
    path('kvr/', views.KVRListView.as_view(), name='kvr_list'),
]
