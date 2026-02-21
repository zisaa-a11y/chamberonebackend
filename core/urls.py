"""
URL configuration for The Chamber One backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def api_root(request):
    """Root API endpoint showing available endpoints."""
    return JsonResponse({
        'message': 'The Chamber One API',
        'endpoints': {
            'admin': '/admin/',
            'auth': '/api/auth/',
            'lawyers': '/api/lawyers/',
            'appointments': '/api/appointments/',
            'cases': '/api/cases/',
            'payments': '/api/payments/',
            'blog': '/api/blog/',
            'landing': '/api/landing/',
        }
    })


urlpatterns = [
    # Root API endpoint
    path('', api_root, name='api_root'),
    
    # Django Admin
    path('admin/', admin.site.urls),
    
    # API Endpoints
    path('api/auth/', include('accounts.urls')),
    path('api/lawyers/', include('lawyers.urls')),
    path('api/appointments/', include('appointments.urls')),
    path('api/cases/', include('cases.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/blog/', include('blog.urls')),
    path('api/landing/', include('landing.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
