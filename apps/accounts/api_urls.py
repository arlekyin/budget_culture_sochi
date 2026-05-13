from django.urls import path
from . import api_views

urlpatterns = [
    path('login/', api_views.LoginAPI.as_view(), name='api_login'),
    path('logout/', api_views.LogoutAPI.as_view(), name='api_logout'),
    path('me/', api_views.MeAPI.as_view(), name='api_me'),
]
