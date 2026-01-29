"""
URL configuration for homefood project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Redirect root URL to buyers home
    path('', RedirectView.as_view(pattern_name='buyers:home', permanent=False)),
    path('', include('apps.accounts.urls')),
    path('cooks/', include('apps.cooks.urls')),
    path('buyers/', include('apps.buyers.urls')),
    path('admin-panel/', include('apps.admin_panel.urls')),
    path('payments/', include('apps.payments.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)






