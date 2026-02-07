"""
API URL Configuration
إعدادات روابط الـ API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views.parties import PartyViewSet
from api.views.invoices import InvoiceViewSet, InvoiceItemViewSet
from api.views.payments import PaymentViewSet
from api.views.ledger import LedgerEntryViewSet
from api.views.reports import SummaryReportView, PartyReportView
from api.views.excel import (
    PartiesExcelExportView,
    PartiesExcelImportView,
    InvoicesExcelExportView,
    PaymentsExcelExportView,
    LedgerExcelExportView,
    FullExcelExportView,
    ExcelTemplateView
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'parties', PartyViewSet, basename='party')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'invoice-items', InvoiceItemViewSet, basename='invoice-item')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'ledger', LedgerEntryViewSet, basename='ledger-entry')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Report endpoints
    path('reports/summary/', SummaryReportView.as_view(), name='report-summary'),
    path('reports/party/<int:pk>/', PartyReportView.as_view(), name='report-party'),
    
    # Excel export endpoints
    path('parties/export/', PartiesExcelExportView.as_view(), name='parties-export'),
    path('parties/import/', PartiesExcelImportView.as_view(), name='parties-import'),
    path('invoices/export/', InvoicesExcelExportView.as_view(), name='invoices-export'),
    path('payments/export/', PaymentsExcelExportView.as_view(), name='payments-export'),
    path('ledger/export/', LedgerExcelExportView.as_view(), name='ledger-export'),
    
    # Full export and templates
    path('excel/export-all/', FullExcelExportView.as_view(), name='excel-export-all'),
    path('excel/template/<str:resource>/', ExcelTemplateView.as_view(), name='excel-template'),
]
