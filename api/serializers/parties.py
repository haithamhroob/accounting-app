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
    status_label = serializers.SerializerMethodField()
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
            'status_label',  # الحقل الجديد للهواة والمحترفين
            'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'balance', 'balance_display', 'party_type_display', 'status_label']
    
    def get_status_label(self, obj):
        """تسمية مخصصة حسب حالة الرصيد"""
        balance = obj.get_balance()
        if balance > 0:
            return "مدين (يجب الحصول على المال)"
        elif balance < 0:
            return "دائن (يجب دفع المال)"
        return "متعادل"
    
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
    status_label = serializers.SerializerMethodField()
    
    class Meta:
        model = Party
        fields = ['id', 'name', 'party_type', 'party_type_display', 'phone', 'balance', 'status_label']
    
    def get_balance(self, obj):
        return str(obj.get_balance())
    
    def get_status_label(self, obj):
        """تسمية مخصصة حسب حالة الرصيد"""
        balance = obj.get_balance()
        if balance > 0:
            return "مدين (يجب الحصول على المال)"
        elif balance < 0:
            return "دائن (يجب دفع المال)"
        return "متعادل"


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
