from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import KOSGU, KVR


class KOSGUListView(LoginRequiredMixin, ListView):
    model = KOSGU
    template_name = 'classifiers/kosgu_list.html'
    context_object_name = 'items'
    queryset = KOSGU.objects.filter(is_active=True).order_by('code')


class KVRListView(LoginRequiredMixin, ListView):
    model = KVR
    template_name = 'classifiers/kvr_list.html'
    context_object_name = 'items'
    queryset = KVR.objects.filter(is_active=True).order_by('code')
