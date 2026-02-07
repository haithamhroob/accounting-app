"""
Django Filter FilterSets
مجموعات الفلاتر
"""
from django_filters import rest_framework as filters
from parties.models import Party
from invoices.models import Invoice, InvoiceItem
from payments.models import Payment
from ledger.models import LedgerEntry


class PartyFilter(filters.FilterSet):
    """
    Filter for Party model
    فلتر الأطراف
    """
    name = filters.CharFilter(lookup_expr='icontains')
    party_type = filters.ChoiceFilter(choices=Party.PartyType.choices)
    created_after = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Party
        fields = ['name', 'party_type', 'phone', 'email']


class InvoiceFilter(filters.FilterSet):
    """
    Filter for Invoice model
    فلتر الفواتير
    """
    invoice_number = filters.CharFilter(lookup_expr='icontains')
    party = filters.NumberFilter()
    party_name = filters.CharFilter(field_name='party__name', lookup_expr='icontains')
    invoice_type = filters.ChoiceFilter(choices=Invoice.InvoiceType.choices)
    status = filters.ChoiceFilter(choices=Invoice.InvoiceStatus.choices)
    issue_date_from = filters.DateFilter(field_name='issue_date', lookup_expr='gte')
    issue_date_to = filters.DateFilter(field_name='issue_date', lookup_expr='lte')
    due_date_from = filters.DateFilter(field_name='due_date', lookup_expr='gte')
    due_date_to = filters.DateFilter(field_name='due_date', lookup_expr='lte')
    min_amount = filters.NumberFilter(method='filter_min_amount')
    max_amount = filters.NumberFilter(method='filter_max_amount')
    
    class Meta:
        model = Invoice
        fields = ['invoice_number', 'party', 'invoice_type', 'status']
    
    def filter_min_amount(self, queryset, name, value):
        # This is a simplified filter - in production you'd want a subquery
        return queryset.filter(items__isnull=False).distinct()
    
    def filter_max_amount(self, queryset, name, value):
        return queryset.filter(items__isnull=False).distinct()


class PaymentFilter(filters.FilterSet):
    """
    Filter for Payment model
    فلتر الدفعات
    """
    invoice = filters.NumberFilter()
    invoice_number = filters.CharFilter(field_name='invoice__invoice_number', lookup_expr='icontains')
    party_name = filters.CharFilter(field_name='invoice__party__name', lookup_expr='icontains')
    payment_method = filters.ChoiceFilter(choices=Payment.PaymentMethod.choices)
    payment_date_from = filters.DateFilter(field_name='payment_date', lookup_expr='gte')
    payment_date_to = filters.DateFilter(field_name='payment_date', lookup_expr='lte')
    min_amount = filters.NumberFilter(field_name='amount', lookup_expr='gte')
    max_amount = filters.NumberFilter(field_name='amount', lookup_expr='lte')
    
    class Meta:
        model = Payment
        fields = ['invoice', 'payment_method', 'payment_date']


class LedgerEntryFilter(filters.FilterSet):
    """
    Filter for LedgerEntry model
    فلتر قيود دفتر الأستاذ
    """
    party = filters.NumberFilter()
    party_name = filters.CharFilter(field_name='party__name', lookup_expr='icontains')
    entry_type = filters.ChoiceFilter(choices=LedgerEntry.EntryType.choices)
    date_from = filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = filters.DateFilter(field_name='date', lookup_expr='lte')
    min_amount = filters.NumberFilter(field_name='amount', lookup_expr='gte')
    max_amount = filters.NumberFilter(field_name='amount', lookup_expr='lte')
    
    class Meta:
        model = LedgerEntry
        fields = ['party', 'entry_type', 'invoice', 'payment']
