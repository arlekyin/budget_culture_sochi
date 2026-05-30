from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('dashboard/', include('apps.monitoring.urls')),
    path('requests/', include('apps.budget_requests.urls')),
    path('institutions/', include('apps.institutions.urls')),
    path('classifiers/', include('apps.classifiers.urls')),
    path('reports/', include('apps.reports.urls')),
    # --- API ---
    path('api/', include('apps.budget_requests.api_urls')),
    path('api/auth/', include('apps.accounts.api_urls')),
    path('api/dashboard/', include('apps.accounts.api_urls_dashboard')),
    path('api/institutions/', include('apps.institutions.api_urls')),
    path('api/monitoring/', include('apps.monitoring.api_urls')),
    path('api/reports/', include('apps.reports.api_urls')),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
