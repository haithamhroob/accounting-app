from django.contrib import admin
from .models import Invoice, InvoiceItem


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    fields = ['description', 'quantity', 'unit_price']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'party', 'invoice_type', 'status', 'issue_date', 'get_total']
    list_filter = ['invoice_type', 'status', 'issue_date']
    search_fields = ['invoice_number', 'party__name']
    ordering = ['-created_at']
    readonly_fields = ['invoice_number', 'created_at', 'updated_at']
    inlines = [InvoiceItemInline]
    
    def get_total(self, obj):
        return obj.get_total()
    get_total.short_description = 'المجموع'


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'description', 'quantity', 'unit_price', 'get_total']
    list_filter = ['invoice__invoice_type']
    search_fields = ['description', 'invoice__invoice_number']
    
    def get_total(self, obj):
        return obj.get_total()
    get_total.short_description = 'المجموع'
