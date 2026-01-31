from django import forms
from django.forms import inlineformset_factory
from .models import Invoice, InvoiceItem


class InvoiceForm(forms.ModelForm):
    """نموذج الفاتورة"""
    
    class Meta:
        model = Invoice
        fields = ['party', 'invoice_type', 'issue_date', 'due_date', 'notes']
        widgets = {
            'party': forms.Select(attrs={
                'class': 'form-select'
            }),
            'invoice_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'issue_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات إضافية (اختياري)'
            }),
        }


class InvoiceItemForm(forms.ModelForm):
    """نموذج بند الفاتورة"""
    
    class Meta:
        model = InvoiceItem
        fields = ['description', 'quantity', 'unit_price']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'وصف البند'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'الكمية'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'سعر الوحدة'
            }),
        }


# Formset for invoice items
InvoiceItemFormSet = inlineformset_factory(
    Invoice,
    InvoiceItem,
    form=InvoiceItemForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False
)
