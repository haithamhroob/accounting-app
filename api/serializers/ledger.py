"""
Ledger Entry Serializers
محولات بيانات دفتر الأستاذ
"""
from rest_framework import serializers
from ledger.models import LedgerEntry
from .parties import PartyListSerializer


class LedgerEntrySerializer(serializers.ModelSerializer):
    """
    Full Ledger Entry serializer
    محول قيد دفتر الأستاذ الكامل
    """
    party_details = PartyListSerializer(source='party', read_only=True)
    entry_type_display = serializers.CharField(source='get_entry_type_display', read_only=True)
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True, allow_null=True)
    
    class Meta:
        model = LedgerEntry
        fields = [
            'id',
            'party',
            'party_details',
            'invoice',
            'invoice_number',
            'payment',
            'entry_type',
            'entry_type_display',
            'amount',
            'date',
            'description',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class LedgerEntryListSerializer(serializers.ModelSerializer):
    """
    Lightweight Ledger Entry serializer for list views
    محول خفيف للقوائم
    """
    party_name = serializers.CharField(source='party.name', read_only=True)
    entry_type_display = serializers.CharField(source='get_entry_type_display', read_only=True)
    
    class Meta:
        model = LedgerEntry
        fields = [
            'id', 'party', 'party_name', 'entry_type', 'entry_type_display',
            'amount', 'date', 'description'
        ]


class LedgerEntryCreateSerializer(serializers.ModelSerializer):
    """
    Ledger Entry serializer for manual creation
    محول القيد للإنشاء اليدوي
    """
    class Meta:
        model = LedgerEntry
        fields = ['party', 'entry_type', 'amount', 'date', 'description']
    
    def validate_entry_type(self, value):
        if value not in ['debit', 'credit']:
            raise serializers.ValidationError("نوع القيد يجب أن يكون 'debit' أو 'credit'")
        return value
