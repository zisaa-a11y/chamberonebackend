"""
URL configuration for The Chamber One backend project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Determine the API URL based on DEBUG setting
if settings.DEBUG:
    api_url = 'http://127.0.0.1:8000/'
else:
    api_url = 'https://backend.thechamberone.com/'

schema_view = get_schema_view(
    openapi.Info(
        title="The Chamber One API",
        default_version='v1',
        description="API documentation for The Chamber One - Legal Services Platform",
        contact=openapi.Contact(email="support@thechamberone.com"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    url=api_url,
)


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
    
    # Swagger Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
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
