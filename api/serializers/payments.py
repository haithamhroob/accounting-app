"""
Payment Serializers
محولات بيانات الدفعات
"""
from rest_framework import serializers
from payments.models import Payment
from .invoices import InvoiceListSerializer


class PaymentSerializer(serializers.ModelSerializer):
    """
    Full Payment serializer
    محول الدفعة الكامل
    """
    invoice_details = InvoiceListSerializer(source='invoice', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id',
            'invoice',
            'invoice_details',
            'amount',
            'payment_method',
            'payment_method_display',
            'payment_date',
            'notes',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class PaymentListSerializer(serializers.ModelSerializer):
    """
    Lightweight Payment serializer for list views
    محول خفيف للقوائم
    """
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    party_name = serializers.CharField(source='invoice.party.name', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'invoice', 'invoice_number', 'party_name',
            'amount', 'payment_method', 'payment_method_display',
            'payment_date'
        ]


class PaymentCreateSerializer(serializers.ModelSerializer):
    """
    Payment serializer for creation
    محول الدفعة للإنشاء
    """
    class Meta:
        model = Payment
        fields = ['invoice', 'amount', 'payment_method', 'payment_date', 'notes']
    
    def validate(self, data):
        invoice = data.get('invoice')
        amount = data.get('amount')
        
        if invoice.status == 'cancelled':
            raise serializers.ValidationError("لا يمكن إضافة دفعة لفاتورة ملغاة")
        
        if invoice.status == 'draft':
            raise serializers.ValidationError("لا يمكن إضافة دفعة لفاتورة مسودة")
        
        remaining = invoice.get_remaining()
        if amount > remaining:
            raise serializers.ValidationError(
                f"المبلغ ({amount}) أكبر من المتبقي ({remaining})"
            )
        
        return data
