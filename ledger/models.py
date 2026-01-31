from django.db import models
from parties.models import Party


class LedgerEntry(models.Model):
    """نموذج قيد دفتر الأستاذ"""
    
    class EntryType(models.TextChoices):
        DEBIT = 'debit', 'مدين'
        CREDIT = 'credit', 'دائن'
    
    party = models.ForeignKey(
        Party,
        on_delete=models.PROTECT,
        related_name='ledger_entries',
        verbose_name='الطرف'
    )
    invoice = models.ForeignKey(
        'invoices.Invoice',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ledger_entries',
        verbose_name='الفاتورة'
    )
    payment = models.ForeignKey(
        'payments.Payment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ledger_entries',
        verbose_name='الدفعة'
    )
    entry_type = models.CharField(
        max_length=10,
        choices=EntryType.choices,
        verbose_name='نوع الحركة'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='المبلغ'
    )
    date = models.DateField(
        verbose_name='التاريخ'
    )
    description = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='الوصف'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء'
    )
    
    class Meta:
        verbose_name = 'قيد'
        verbose_name_plural = 'القيود'
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.get_entry_type_display()} - {self.amount} - {self.party.name}"
