from django.db import models
from django.urls import reverse
from decimal import Decimal


class Party(models.Model):
    """نموذج الطرف (عميل أو مورّد)"""
    
    class PartyType(models.TextChoices):
        CUSTOMER = 'customer', 'عميل'
        SUPPLIER = 'supplier', 'مورّد'
    
    name = models.CharField(
        max_length=255,
        verbose_name='الاسم'
    )
    party_type = models.CharField(
        max_length=20,
        choices=PartyType.choices,
        verbose_name='النوع'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='رقم الهاتف'
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='البريد الإلكتروني'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإضافة'
    )
    
    class Meta:
        verbose_name = 'طرف'
        verbose_name_plural = 'الأطراف'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_party_type_display()})"
    
    def get_absolute_url(self):
        return reverse('parties:detail', kwargs={'pk': self.pk})
    
    def get_balance(self):
        """حساب رصيد الطرف من دفتر الأستاذ"""
        from ledger.models import LedgerEntry
        
        entries = LedgerEntry.objects.filter(party=self)
        debit = entries.filter(entry_type='debit').aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0')
        credit = entries.filter(entry_type='credit').aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0')
        
        return debit - credit
    
    def get_balance_display(self):
        """عرض الرصيد مع الوصف"""
        balance = self.get_balance()
        if balance > 0:
            return f"له علينا: {balance}"
        elif balance < 0:
            return f"لنا عليه: {abs(balance)}"
        return "لا يوجد رصيد"
