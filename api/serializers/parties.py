"""
Party Serializers
محولات بيانات الأطراف (العملاء والموردين)
"""
from rest_framework import serializers
from parties.models import Party
from decimal import Decimal


class PartySerializer(serializers.ModelSerializer):
    """
    Full Party serializer with all fields
    محول كامل للطرف مع جميع الحقول
    """
    balance = serializers.SerializerMethodField()
    balance_display = serializers.SerializerMethodField()
    party_type_display = serializers.CharField(source='get_party_type_display', read_only=True)
    
    class Meta:
        model = Party
        fields = [
            'id',
            'name',
            'party_type',
            'party_type_display',
            'phone',
            'email',
            'balance',
            'balance_display',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'balance', 'balance_display', 'party_type_display']
    
    def get_balance(self, obj):
        """Get the party's current balance"""
        return str(obj.get_balance())
    
    def get_balance_display(self, obj):
        """Get the party's balance with Arabic description"""
        return obj.get_balance_display()


class PartyListSerializer(serializers.ModelSerializer):
    """
    Lightweight Party serializer for list views
    محول خفيف للقوائم
    """
    party_type_display = serializers.CharField(source='get_party_type_display', read_only=True)
    balance = serializers.SerializerMethodField()
    
    class Meta:
        model = Party
        fields = ['id', 'name', 'party_type', 'party_type_display', 'phone', 'balance']
    
    def get_balance(self, obj):
        return str(obj.get_balance())


class PartyCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Party serializer for create/update operations
    محول للإنشاء والتحديث
    """
    class Meta:
        model = Party
        fields = ['name', 'party_type', 'phone', 'email']
    
    def validate_party_type(self, value):
        if value not in ['customer', 'supplier']:
            raise serializers.ValidationError("نوع الطرف يجب أن يكون 'customer' أو 'supplier'")
        return value
