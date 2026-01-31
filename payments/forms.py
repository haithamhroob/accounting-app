from django import forms
from decimal import Decimal
from .models import Payment


class PaymentForm(forms.ModelForm):
    """نموذج الدفعة"""
    
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'payment_date', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'أدخل المبلغ'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select'
            }),
            'payment_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'ملاحظات (اختياري)'
            }),
        }
    
    def __init__(self, *args, invoice=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.invoice = invoice
        
        if invoice:
            remaining = invoice.get_remaining()
            self.fields['amount'].widget.attrs['max'] = str(remaining)
            self.fields['amount'].help_text = f'المبلغ المتبقي: {remaining}'
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        
        if amount is None or amount <= Decimal('0'):
            raise forms.ValidationError('يجب أن يكون المبلغ أكبر من صفر')
        
        if self.invoice:
            remaining = self.invoice.get_remaining()
            if amount > remaining:
                raise forms.ValidationError(
                    f'المبلغ أكبر من المتبقي ({remaining})'
                )
        
        return amount
