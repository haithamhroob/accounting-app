"""
Invoice Serializers
محولات بيانات الفواتير
"""
from rest_framework import serializers
from invoices.models import Invoice, InvoiceItem
from .parties import PartyListSerializer


class InvoiceItemSerializer(serializers.ModelSerializer):
    """
    Invoice Item serializer
    محول بند الفاتورة
    """
    total = serializers.SerializerMethodField()
    
    class Meta:
        model = InvoiceItem
        fields = ['id', 'invoice', 'description', 'quantity', 'unit_price', 'total']
        read_only_fields = ['id', 'total']
    
    def get_total(self, obj):
        return str(obj.get_total())


class InvoiceItemCreateSerializer(serializers.ModelSerializer):
    """
    Invoice Item serializer for creation (without invoice field)
    محول بند الفاتورة للإنشاء
    """
    class Meta:
        model = InvoiceItem
        fields = ['description', 'quantity', 'unit_price']


class InvoiceSerializer(serializers.ModelSerializer):
    """
    Full Invoice serializer with nested items
    محول الفاتورة الكامل مع البنود
    """
    party_details = PartyListSerializer(source='party', read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)
    invoice_type_display = serializers.CharField(source='get_invoice_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total = serializers.SerializerMethodField()
    paid_amount = serializers.SerializerMethodField()
    remaining = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_issue = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = [
            'id',
            'invoice_number',
            'party',
            'party_details',
            'invoice_type',
            'invoice_type_display',
            'issue_date',
            'due_date',
            'status',
            'status_display',
            'notes',
            'items',
            'total',
            'paid_amount',
            'remaining',
            'can_edit',
            'can_issue',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'invoice_number', 'created_at', 'updated_at',
            'total', 'paid_amount', 'remaining', 'can_edit', 'can_issue'
        ]
    
    def get_total(self, obj):
        return str(obj.get_total())
    
    def get_paid_amount(self, obj):
        return str(obj.get_paid_amount())
    
    def get_remaining(self, obj):
        return str(obj.get_remaining())
    
    def get_can_edit(self, obj):
        return obj.can_edit()
    
    def get_can_issue(self, obj):
        return obj.can_issue()


class InvoiceListSerializer(serializers.ModelSerializer):
    """
    Lightweight Invoice serializer for list views
    محول خفيف للقوائم
    """
    party_name = serializers.CharField(source='party.name', read_only=True)
    invoice_type_display = serializers.CharField(source='get_invoice_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'party', 'party_name',
            'invoice_type', 'invoice_type_display',
            'issue_date', 'status', 'status_display', 'total'
        ]
    
    def get_total(self, obj):
        return str(obj.get_total())


class InvoiceCreateSerializer(serializers.ModelSerializer):
    """
    Invoice serializer for creation with nested items
    محول الفاتورة للإنشاء مع البنود
    """
    items = InvoiceItemCreateSerializer(many=True, required=False)
    
    class Meta:
        model = Invoice
        fields = ['party', 'invoice_type', 'issue_date', 'due_date', 'notes', 'items']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        invoice = Invoice.objects.create(**validated_data)
        
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)
        
        return invoice


class InvoiceUpdateSerializer(serializers.ModelSerializer):
    """
    Invoice serializer for updates
    محول الفاتورة للتحديث
    """
    class Meta:
        model = Invoice
        fields = ['party', 'invoice_type', 'issue_date', 'due_date', 'notes']
    
    def validate(self, data):
        if self.instance and not self.instance.can_edit():
            raise serializers.ValidationError("لا يمكن تعديل فاتورة صادرة أو مدفوعة")
        return data
