from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from .models import Institution, BudgetLimit


class InstitutionListView(LoginRequiredMixin, ListView):
    model = Institution
    template_name = 'institutions/list.html'
    context_object_name = 'institutions'
    queryset = Institution.objects.filter(is_active=True).order_by('short_name')


class InstitutionDetailView(LoginRequiredMixin, DetailView):
    model = Institution
    template_name = 'institutions/detail.html'
    context_object_name = 'institution'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['limits'] = BudgetLimit.objects.filter(
            institution=self.object
        ).order_by('-year')
        ctx['requests'] = self.object.requests.order_by('-created_at')[:10]
        return ctx
