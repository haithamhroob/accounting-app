"""
Party ViewSet
عرض الأطراف (العملاء والموردين)
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from parties.models import Party
from api.serializers.parties import (
    PartySerializer, 
    PartyListSerializer, 
    PartyCreateUpdateSerializer
)
from api.filters import PartyFilter
from api.permissions import RoleBasedPermission
from api.pagination import StandardResultsSetPagination


@extend_schema_view(
    list=extend_schema(
        summary="قائمة الأطراف",
        description="الحصول على قائمة جميع العملاء والموردين مع إمكانية الفلترة والبحث",
        tags=["الأطراف - Parties"]
    ),
    retrieve=extend_schema(
        summary="تفاصيل طرف",
        description="الحصول على تفاصيل عميل أو مورد محدد",
        tags=["الأطراف - Parties"]
    ),
    create=extend_schema(
        summary="إضافة طرف جديد",
        description="إنشاء عميل أو مورد جديد",
        tags=["الأطراف - Parties"]
    ),
    update=extend_schema(
        summary="تحديث طرف",
        description="تحديث بيانات عميل أو مورد",
        tags=["الأطراف - Parties"]
    ),
    partial_update=extend_schema(
        summary="تحديث جزئي لطرف",
        description="تحديث بعض بيانات عميل أو مورد",
        tags=["الأطراف - Parties"]
    ),
    destroy=extend_schema(
        summary="حذف طرف",
        description="حذف عميل أو مورد (يتطلب صلاحيات مسؤول)",
        tags=["الأطراف - Parties"]
    ),
)
class PartyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Party CRUD operations
    واجهة عرض لعمليات CRUD على الأطراف
    """
    queryset = Party.objects.all()
    permission_classes = [RoleBasedPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PartyFilter
    search_fields = ['name', 'phone', 'email']
    ordering_fields = ['name', 'created_at', 'party_type']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PartyListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PartyCreateUpdateSerializer
        return PartySerializer
    
    @extend_schema(
        summary="رصيد الطرف",
        description="الحصول على رصيد طرف محدد مع تفاصيل الحساب",
        tags=["الأطراف - Parties"],
        responses={200: {
            "type": "object",
            "properties": {
                "party_id": {"type": "integer"},
                "party_name": {"type": "string"},
                "balance": {"type": "string"},
                "balance_display": {"type": "string"},
            }
        }}
    )
    @action(detail=True, methods=['get'])
    def balance(self, request, pk=None):
        """
        Get party balance details
        الحصول على تفاصيل رصيد الطرف
        """
        party = self.get_object()
        return Response({
            'party_id': party.id,
            'party_name': party.name,
            'balance': str(party.get_balance()),
            'balance_display': party.get_balance_display()
        })
