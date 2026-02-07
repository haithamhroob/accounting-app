"""
Ledger Entry ViewSet
عرض قيود دفتر الأستاذ
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, extend_schema_view

from ledger.models import LedgerEntry
from api.serializers.ledger import (
    LedgerEntrySerializer,
    LedgerEntryListSerializer,
    LedgerEntryCreateSerializer
)
from api.filters import LedgerEntryFilter
from api.permissions import RoleBasedPermission
from api.pagination import StandardResultsSetPagination


@extend_schema_view(
    list=extend_schema(
        summary="قائمة القيود",
        description="الحصول على قائمة جميع قيود دفتر الأستاذ",
        tags=["دفتر الأستاذ - Ledger"]
    ),
    retrieve=extend_schema(
        summary="تفاصيل قيد",
        description="الحصول على تفاصيل قيد محدد",
        tags=["دفتر الأستاذ - Ledger"]
    ),
    create=extend_schema(
        summary="إنشاء قيد يدوي",
        description="إنشاء قيد يدوي في دفتر الأستاذ",
        tags=["دفتر الأستاذ - Ledger"]
    ),
)
class LedgerEntryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for LedgerEntry operations
    واجهة عرض لعمليات دفتر الأستاذ
    
    Note: Ledger entries are mostly created automatically.
    Manual creation is allowed but update/delete is restricted.
    """
    queryset = LedgerEntry.objects.select_related('party', 'invoice', 'payment')
    permission_classes = [RoleBasedPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = LedgerEntryFilter
    search_fields = ['party__name', 'description']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date', '-created_at']
    
    # Only allow list, retrieve, and create (no update/delete for audit trail)
    http_method_names = ['get', 'post', 'head', 'options']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return LedgerEntryListSerializer
        elif self.action == 'create':
            return LedgerEntryCreateSerializer
        return LedgerEntrySerializer
