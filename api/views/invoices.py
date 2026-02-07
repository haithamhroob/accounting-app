"""
Invoice ViewSet
عرض الفواتير
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, extend_schema_view

from invoices.models import Invoice, InvoiceItem
from api.serializers.invoices import (
    InvoiceSerializer,
    InvoiceListSerializer,
    InvoiceCreateSerializer,
    InvoiceUpdateSerializer,
    InvoiceItemSerializer,
    InvoiceItemCreateSerializer
)
from api.filters import InvoiceFilter
from api.permissions import RoleBasedPermission
from api.pagination import StandardResultsSetPagination


@extend_schema_view(
    list=extend_schema(
        summary="قائمة الفواتير",
        description="الحصول على قائمة جميع الفواتير مع إمكانية الفلترة",
        tags=["الفواتير - Invoices"]
    ),
    retrieve=extend_schema(
        summary="تفاصيل فاتورة",
        description="الحصول على تفاصيل فاتورة محددة مع البنود",
        tags=["الفواتير - Invoices"]
    ),
    create=extend_schema(
        summary="إنشاء فاتورة",
        description="إنشاء فاتورة جديدة مع البنود",
        tags=["الفواتير - Invoices"]
    ),
    update=extend_schema(
        summary="تحديث فاتورة",
        description="تحديث فاتورة (مسودة فقط)",
        tags=["الفواتير - Invoices"]
    ),
    partial_update=extend_schema(
        summary="تحديث جزئي لفاتورة",
        description="تحديث بعض بيانات فاتورة",
        tags=["الفواتير - Invoices"]
    ),
    destroy=extend_schema(
        summary="حذف فاتورة",
        description="حذف فاتورة (مسودة فقط، يتطلب صلاحيات مسؤول)",
        tags=["الفواتير - Invoices"]
    ),
)
class InvoiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Invoice CRUD operations
    واجهة عرض لعمليات CRUD على الفواتير
    """
    queryset = Invoice.objects.select_related('party').prefetch_related('items', 'payments')
    permission_classes = [RoleBasedPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = InvoiceFilter
    search_fields = ['invoice_number', 'party__name', 'notes']
    ordering_fields = ['invoice_number', 'issue_date', 'created_at', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return InvoiceListSerializer
        elif self.action == 'create':
            return InvoiceCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return InvoiceUpdateSerializer
        return InvoiceSerializer
    
    def destroy(self, request, *args, **kwargs):
        invoice = self.get_object()
        if not invoice.can_edit():
            return Response(
                {'error': 'لا يمكن حذف فاتورة صادرة أو مدفوعة'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)
    
    @extend_schema(
        summary="إصدار فاتورة",
        description="تحويل فاتورة من مسودة إلى صادرة",
        tags=["الفواتير - Invoices"],
        responses={200: InvoiceSerializer}
    )
    @action(detail=True, methods=['post'])
    def issue(self, request, pk=None):
        """
        Issue a draft invoice
        إصدار فاتورة مسودة
        """
        invoice = self.get_object()
        
        if not invoice.can_issue():
            return Response(
                {'error': 'لا يمكن إصدار هذه الفاتورة. تأكد من أنها مسودة وتحتوي على بنود.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invoice.status = Invoice.InvoiceStatus.ISSUED
        invoice.save()
        
        # Create ledger entry for the invoice
        from ledger.services import create_invoice_entry
        create_invoice_entry(invoice)
        
        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data)
    
    @extend_schema(
        summary="إلغاء فاتورة",
        description="إلغاء فاتورة صادرة",
        tags=["الفواتير - Invoices"],
        responses={200: InvoiceSerializer}
    )
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel an issued invoice
        إلغاء فاتورة صادرة
        """
        invoice = self.get_object()
        
        if invoice.status == Invoice.InvoiceStatus.CANCELLED:
            return Response(
                {'error': 'الفاتورة ملغاة بالفعل'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if invoice.get_paid_amount() > 0:
            return Response(
                {'error': 'لا يمكن إلغاء فاتورة تم دفعها. يجب استرداد الدفعات أولاً.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invoice.status = Invoice.InvoiceStatus.CANCELLED
        invoice.save()
        
        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data)
    
    @extend_schema(
        summary="بنود الفاتورة",
        description="إضافة بند جديد للفاتورة",
        tags=["الفواتير - Invoices"],
        request=InvoiceItemCreateSerializer,
        responses={201: InvoiceItemSerializer}
    )
    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """
        Add an item to an invoice
        إضافة بند للفاتورة
        """
        invoice = self.get_object()
        
        if not invoice.can_edit():
            return Response(
                {'error': 'لا يمكن إضافة بنود لفاتورة صادرة'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = InvoiceItemCreateSerializer(data=request.data)
        if serializer.is_valid():
            item = InvoiceItem.objects.create(invoice=invoice, **serializer.validated_data)
            return Response(InvoiceItemSerializer(item).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InvoiceItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for InvoiceItem CRUD operations
    واجهة عرض لعمليات CRUD على بنود الفواتير
    """
    queryset = InvoiceItem.objects.select_related('invoice', 'invoice__party')
    serializer_class = InvoiceItemSerializer
    permission_classes = [RoleBasedPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['description']
    ordering = ['-id']
    
    def destroy(self, request, *args, **kwargs):
        item = self.get_object()
        if not item.invoice.can_edit():
            return Response(
                {'error': 'لا يمكن حذف بند من فاتورة صادرة'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)
