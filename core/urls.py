"""
core URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse, HttpResponse
from django.db import connection
from django.views.generic import TemplateView
from django.conf import settings
import platform, socket, os, django

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


def docker_status(request):
    """صفحة إثبات تشغيل التطبيق داخل Docker"""
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT version()')
            db_version = cursor.fetchone()[0].split(',')[0]
        db_status = '✅ Connected'
        db_color  = '#22c55e'
    except Exception as e:
        db_version = str(e)
        db_status  = '❌ Disconnected'
        db_color   = '#ef4444'

    container_name = socket.gethostname()
    os_info        = f"{platform.system()} {platform.release()}"
    python_version = platform.python_version()
    django_version = django.get_version()
    running_in_docker = os.path.exists('/.dockerenv')
    docker_badge = '<span style="background:#2563eb;color:#fff;padding:4px 14px;border-radius:20px;font-size:13px;">🐳 Inside Docker</span>' if running_in_docker else '<span style="background:#f59e0b;color:#fff;padding:4px 14px;border-radius:20px;font-size:13px;">⚠️ Not in Docker</span>'

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Docker Status</title>
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{ font-family: 'Segoe UI', sans-serif; background: #f1f5f9; color: #1e293b; display: flex; align-items: center; justify-content: center; min-height: 100vh; }}
            .card {{ background: #ffffff; border-radius: 16px; padding: 40px; width: 520px; box-shadow: 0 8px 30px rgba(0,0,0,0.10); }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .header h1 {{ font-size: 28px; color: #0ea5e9; }}
            .header p {{ color: #64748b; margin-top: 6px; font-size: 14px; }}
            .badge {{ display: flex; justify-content: center; margin: 16px 0 28px; }}
            .row {{ display: flex; justify-content: space-between; align-items: center; padding: 14px 0; border-bottom: 1px solid #e2e8f0; }}
            .row:last-child {{ border-bottom: none; }}
            .label {{ color: #64748b; font-size: 14px; }}
            .value {{ color: #0f172a; font-size: 14px; font-weight: 600; text-align: right; max-width: 280px; word-break: break-all; }}
            .db-status {{ color: {db_color}; font-weight: 700; }}
            .footer {{ text-align: center; margin-top: 28px; color: #94a3b8; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="header">
                <h1>🐳 Docker Status</h1>
                <p>Accounting App — Container Info</p>
            </div>
            <div class="badge">{docker_badge}</div>

            <div class="row"><span class="label">Container Hostname</span><span class="value">{container_name}</span></div>
            <div class="row"><span class="label">Operating System</span><span class="value">{os_info}</span></div>
            <div class="row"><span class="label">Python Version</span><span class="value">{python_version}</span></div>
            <div class="row"><span class="label">Django Version</span><span class="value">{django_version}</span></div>
            <div class="row"><span class="label">Database</span><span class="value db-status">{db_status}</span></div>
            <div class="row"><span class="label">DB Engine</span><span class="value">{db_version}</span></div>

            <div class="footer">This page proves the app is running inside a Docker container ✅</div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)


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
    path('docker/', docker_status, name='docker_status'),
    
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
