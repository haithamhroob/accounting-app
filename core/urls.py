"""
core URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.db import connection
from django.views.generic import TemplateView
from django.conf import settings

# JWT Authentication
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# OpenAPI/Swagger
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


def health_check(request):
    """نقطة فحص صحة التطبيق"""
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        db_status = 'connected'
    except Exception:
        db_status = 'disconnected'
    
    return JsonResponse({
        'status': 'ok' if db_status == 'connected' else 'error',
        'database': db_status
    })


class HomeView(TemplateView):
    template_name = 'home.html'


# Manual OpenAPI YAML serving
class ManualSwaggerView(TemplateView):
    """Swagger UI for manual OpenAPI YAML"""
    template_name = 'swagger_manual.html'


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Home and Health
    path('', HomeView.as_view(), name='home'),
    path('health', health_check, name='health_check'),
    
    # Existing HTML views (not affected)
    path('parties/', include('parties.urls')),
    path('invoices/', include('invoices.urls')),
    path('payments/', include('payments.urls')),
    path('reports/', include('reports.urls')),
    
    # ==========================================================================
    # API v1 Routes
    # ==========================================================================
    path('api/v1/', include('api.urls')),
    
    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # ==========================================================================
    # API Documentation (Auto-generated)
    # ==========================================================================
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Manual OpenAPI Documentation
    path('docs/manual/', ManualSwaggerView.as_view(), name='swagger-manual'),
]

# Arabic Admin Site Headers
admin.site.site_header = 'لوحة إدارة النظام المحاسبي'
admin.site.site_title = 'النظام المحاسبي'
admin.site.index_title = 'الإدارة'

# =============================================================================
# Conditional API Documentation Access
# =============================================================================
# In production, you might want to restrict access to API docs
# This is handled by the API_DOCS_PUBLIC setting in settings.py
