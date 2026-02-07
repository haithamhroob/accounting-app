"""
Excel Import/Export Views
عرض استيراد/تصدير Excel
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from parties.models import Party
from invoices.models import Invoice
from payments.models import Payment
from ledger.models import LedgerEntry
from api.permissions import RoleBasedPermission
from api.excel_utils import (
    create_parties_excel,
    create_invoices_excel,
    create_payments_excel,
    create_ledger_excel,
    create_full_export_excel,
    create_import_template,
    parse_parties_excel,
    EXCEL_AVAILABLE
)


class ExcelExportMixin:
    """Mixin for Excel export functionality"""
    
    def get_excel_response(self, excel_file, filename):
        """Create HTTP response for Excel file download"""
        response = HttpResponse(
            excel_file.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class PartiesExcelExportView(ExcelExportMixin, APIView):
    """Export parties to Excel"""
    permission_classes = [RoleBasedPermission]
    
    @extend_schema(
        summary="تصدير الأطراف إلى Excel",
        description="تحميل جميع العملاء والموردين كملف Excel",
        tags=["Excel - استيراد/تصدير"],
        parameters=[
            OpenApiParameter(name='party_type', type=str, description='فلترة حسب النوع (customer/supplier)')
        ]
    )
    def get(self, request):
        if not EXCEL_AVAILABLE:
            return Response(
                {'error': 'Excel dependencies not installed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        queryset = Party.objects.all()
        party_type = request.GET.get('party_type')
        if party_type:
            queryset = queryset.filter(party_type=party_type)
        
        excel_file = create_parties_excel(queryset)
        return self.get_excel_response(excel_file, 'parties.xlsx')


class PartiesExcelImportView(APIView):
    """Import parties from Excel"""
    permission_classes = [RoleBasedPermission]
    parser_classes = [MultiPartParser, FormParser]
    
    @extend_schema(
        summary="استيراد الأطراف من Excel",
        description="رفع ملف Excel لإضافة عملاء وموردين جديدة",
        tags=["Excel - استيراد/تصدير"],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {'type': 'string', 'format': 'binary'}
                }
            }
        }
    )
    def post(self, request):
        if not EXCEL_AVAILABLE:
            return Response(
                {'error': 'Excel dependencies not installed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        file = request.FILES.get('file')
        if not file:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            parties_data, errors = parse_parties_excel(file)
            
            created_parties = []
            for party_data in parties_data:
                party = Party.objects.create(**party_data)
                created_parties.append({
                    'id': party.id,
                    'name': party.name,
                    'party_type': party.party_type
                })
            
            return Response({
                'message': f'تم استيراد {len(created_parties)} طرف بنجاح',
                'created': created_parties,
                'errors': errors
            }, status=status.HTTP_201_CREATED if created_parties else status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response(
                {'error': f'Error processing file: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class InvoicesExcelExportView(ExcelExportMixin, APIView):
    """Export invoices to Excel"""
    permission_classes = [RoleBasedPermission]
    
    @extend_schema(
        summary="تصدير الفواتير إلى Excel",
        description="تحميل جميع الفواتير كملف Excel",
        tags=["Excel - استيراد/تصدير"],
        parameters=[
            OpenApiParameter(name='invoice_type', type=str, description='فلترة حسب النوع (sale/purchase)'),
            OpenApiParameter(name='status', type=str, description='فلترة حسب الحالة'),
        ]
    )
    def get(self, request):
        if not EXCEL_AVAILABLE:
            return Response(
                {'error': 'Excel dependencies not installed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        queryset = Invoice.objects.select_related('party').prefetch_related('items', 'payments')
        
        invoice_type = request.GET.get('invoice_type')
        if invoice_type:
            queryset = queryset.filter(invoice_type=invoice_type)
        
        status_filter = request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        excel_file = create_invoices_excel(queryset)
        return self.get_excel_response(excel_file, 'invoices.xlsx')


class PaymentsExcelExportView(ExcelExportMixin, APIView):
    """Export payments to Excel"""
    permission_classes = [RoleBasedPermission]
    
    @extend_schema(
        summary="تصدير الدفعات إلى Excel",
        description="تحميل جميع الدفعات كملف Excel",
        tags=["Excel - استيراد/تصدير"]
    )
    def get(self, request):
        if not EXCEL_AVAILABLE:
            return Response(
                {'error': 'Excel dependencies not installed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        queryset = Payment.objects.select_related('invoice', 'invoice__party')
        excel_file = create_payments_excel(queryset)
        return self.get_excel_response(excel_file, 'payments.xlsx')


class LedgerExcelExportView(ExcelExportMixin, APIView):
    """Export ledger entries to Excel"""
    permission_classes = [RoleBasedPermission]
    
    @extend_schema(
        summary="تصدير دفتر الأستاذ إلى Excel",
        description="تحميل جميع قيود دفتر الأستاذ كملف Excel",
        tags=["Excel - استيراد/تصدير"]
    )
    def get(self, request):
        if not EXCEL_AVAILABLE:
            return Response(
                {'error': 'Excel dependencies not installed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        queryset = LedgerEntry.objects.select_related('party', 'invoice')
        excel_file = create_ledger_excel(queryset)
        return self.get_excel_response(excel_file, 'ledger.xlsx')


class FullExcelExportView(ExcelExportMixin, APIView):
    """Export all data to a single Excel file with multiple sheets"""
    permission_classes = [RoleBasedPermission]
    
    @extend_schema(
        summary="تصدير جميع البيانات إلى Excel",
        description="تحميل جميع البيانات (الأطراف، الفواتير، الدفعات، دفتر الأستاذ) في ملف Excel واحد",
        tags=["Excel - استيراد/تصدير"]
    )
    def get(self, request):
        if not EXCEL_AVAILABLE:
            return Response(
                {'error': 'Excel dependencies not installed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        parties = Party.objects.all()
        invoices = Invoice.objects.select_related('party').prefetch_related('items', 'payments')
        payments = Payment.objects.select_related('invoice', 'invoice__party')
        ledger_entries = LedgerEntry.objects.select_related('party', 'invoice')
        
        excel_file = create_full_export_excel(parties, invoices, payments, ledger_entries)
        return self.get_excel_response(excel_file, 'accounting_data.xlsx')


class ExcelTemplateView(ExcelExportMixin, APIView):
    """Download import template"""
    permission_classes = [RoleBasedPermission]
    
    @extend_schema(
        summary="تحميل قالب الاستيراد",
        description="تحميل قالب Excel للاستيراد حسب نوع البيانات",
        tags=["Excel - استيراد/تصدير"],
        parameters=[
            OpenApiParameter(
                name='resource',
                type=str,
                location=OpenApiParameter.PATH,
                description='نوع البيانات (parties/invoices/payments)'
            )
        ]
    )
    def get(self, request, resource):
        if not EXCEL_AVAILABLE:
            return Response(
                {'error': 'Excel dependencies not installed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        if resource not in ['parties', 'invoices', 'payments']:
            return Response(
                {'error': f'Unknown resource type: {resource}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        excel_file = create_import_template(resource)
        return self.get_excel_response(excel_file, f'{resource}_template.xlsx')
