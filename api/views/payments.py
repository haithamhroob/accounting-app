"""
Payment ViewSet
عرض الدفعات
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, extend_schema_view

from payments.models import Payment
from api.serializers.payments import (
    PaymentSerializer,
    PaymentListSerializer,
    PaymentCreateSerializer
)
from api.filters import PaymentFilter
from api.permissions import RoleBasedPermission
from api.pagination import StandardResultsSetPagination


@extend_schema_view(
    list=extend_schema(
        summary="قائمة الدفعات",
        description="الحصول على قائمة جميع الدفعات",
        tags=["الدفعات - Payments"]
    ),
    retrieve=extend_schema(
        summary="تفاصيل دفعة",
        description="الحصول على تفاصيل دفعة محددة",
        tags=["الدفعات - Payments"]
    ),
    create=extend_schema(
        summary="تسجيل دفعة",
        description="تسجيل دفعة جديدة لفاتورة",
        tags=["الدفعات - Payments"]
    ),
    destroy=extend_schema(
        summary="حذف دفعة",
        description="حذف دفعة (يتطلب صلاحيات مسؤول)",
        tags=["الدفعات - Payments"]
    ),
)
class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Payment CRUD operations
    واجهة عرض لعمليات CRUD على الدفعات
    """
    queryset = Payment.objects.select_related('invoice', 'invoice__party')
    permission_classes = [RoleBasedPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PaymentFilter
    search_fields = ['invoice__invoice_number', 'invoice__party__name', 'notes']
    ordering_fields = ['payment_date', 'amount', 'created_at']
    ordering = ['-payment_date', '-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PaymentListSerializer
        elif self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer
    
    # Payments should not be updated, only created or deleted
    http_method_names = ['get', 'post', 'delete', 'head', 'options']
    
    @extend_schema(
        summary="استرداد دفعة",
        description="استرداد دفعة (إنشاء قيد عكسي)",
        tags=["الدفعات - Payments"],
        responses={200: {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "refunded_amount": {"type": "string"},
                "invoice_status": {"type": "string"},
            }
        }}
    )
    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """
        Refund a payment
        استرداد دفعة
        """
        payment = self.get_object()
        invoice = payment.invoice
        
        # Create reverse ledger entry
        from ledger.models import LedgerEntry
        from ledger.services import create_refund_entry
        
        create_refund_entry(payment)
        
        # Delete the payment
        refunded_amount = payment.amount
        payment.delete()
        
        # Update invoice status
        invoice.update_status()
        
        return Response({
            'message': 'تم استرداد الدفعة بنجاح',
            'refunded_amount': str(refunded_amount),
            'invoice_status': invoice.get_status_display()
        })
