from django.contrib import admin
from .models import LedgerEntry


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ['party', 'entry_type', 'amount', 'date', 'invoice', 'payment', 'description']
    list_filter = ['entry_type', 'date']
    search_fields = ['party__name', 'invoice__invoice_number', 'description']
    ordering = ['-date', '-created_at']
    date_hierarchy = 'date'
    readonly_fields = ['party', 'invoice', 'payment', 'entry_type', 'amount', 'date', 'description', 'created_at']
    
    def has_add_permission(self, request):
        # القيود تُنشأ تلقائياً فقط
        return False
    
    def has_change_permission(self, request, obj=None):
        # القيود للقراءة فقط
        return False
    
    def has_delete_permission(self, request, obj=None):
        # لا يمكن حذف القيود
        return False
