"""
core URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.db import connection
from django.views.generic import TemplateView


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


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('health', health_check, name='health_check'),
    path('parties/', include('parties.urls')),
    path('invoices/', include('invoices.urls')),
    path('payments/', include('payments.urls')),
    path('reports/', include('reports.urls')),
]

# Arabic Admin Site Headers
admin.site.site_header = 'لوحة إدارة النظام المحاسبي'
admin.site.site_title = 'النظام المحاسبي'
admin.site.index_title = 'الإدارة'
