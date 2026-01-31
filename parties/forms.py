from django import forms
from .models import Party


class PartyForm(forms.ModelForm):
    """نموذج إضافة/تعديل طرف"""
    
    class Meta:
        model = Party
        fields = ['name', 'party_type', 'phone', 'email']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل اسم الطرف'
            }),
            'party_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الهاتف (اختياري)'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'البريد الإلكتروني (اختياري)'
            }),
        }
