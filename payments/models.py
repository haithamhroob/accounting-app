from django.db import models
from invoices.models import Invoice


class Payment(models.Model):
    """نموذج الدفعة"""
    
    class PaymentMethod(models.TextChoices):
        CASH = 'cash', 'نقدي'
        CARD = 'card', 'بطاقة'
        TRANSFER = 'transfer', 'تحويل بنكي'
    
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.PROTECT,
        related_name='payments',
        verbose_name='الفاتورة'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='المبلغ'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        verbose_name='طريقة الدفع'
    )
    payment_date = models.DateField(
        verbose_name='تاريخ الدفع'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='ملاحظات'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء'
    )
    
    class Meta:
        verbose_name = 'دفعة'
        verbose_name_plural = 'الدفعات'
        ordering = ['-payment_date', '-created_at']
    
    def __str__(self):
        return f"دفعة {self.amount} - {self.invoice.invoice_number}"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # إنشاء قيد دفتر الأستاذ
            from ledger.services import create_payment_entry
            create_payment_entry(self)
        
        # تحديث حالة الفاتورة
        self.invoice.update_status()
