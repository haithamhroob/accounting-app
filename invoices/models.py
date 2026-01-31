from django.db import models
from django.urls import reverse
from decimal import Decimal
from parties.models import Party


class Invoice(models.Model):
    """نموذج الفاتورة"""
    
    class InvoiceType(models.TextChoices):
        SALE = 'sale', 'بيع'
        PURCHASE = 'purchase', 'شراء'
    
    class InvoiceStatus(models.TextChoices):
        DRAFT = 'draft', 'مسودة'
        ISSUED = 'issued', 'صادرة'
        PAID = 'paid', 'مدفوعة'
        PARTIAL = 'partial', 'مدفوعة جزئيًا'
        CANCELLED = 'cancelled', 'ملغاة'
    
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='رقم الفاتورة'
    )
    party = models.ForeignKey(
        Party,
        on_delete=models.PROTECT,
        related_name='invoices',
        verbose_name='الطرف'
    )
    invoice_type = models.CharField(
        max_length=20,
        choices=InvoiceType.choices,
        verbose_name='نوع الفاتورة'
    )
    issue_date = models.DateField(
        verbose_name='تاريخ الإصدار'
    )
    due_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='تاريخ الاستحقاق'
    )
    status = models.CharField(
        max_length=20,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.DRAFT,
        verbose_name='الحالة'
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
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاريخ التعديل'
    )
    
    class Meta:
        verbose_name = 'فاتورة'
        verbose_name_plural = 'الفواتير'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"فاتورة {self.invoice_number} - {self.party.name}"
    
    def get_absolute_url(self):
        return reverse('invoices:detail', kwargs={'pk': self.pk})
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # توليد رقم فاتورة تلقائي
            last_invoice = Invoice.objects.order_by('-id').first()
            if last_invoice:
                try:
                    last_num = int(last_invoice.invoice_number.split('-')[-1])
                    self.invoice_number = f"INV-{last_num + 1:06d}"
                except (ValueError, IndexError):
                    self.invoice_number = f"INV-{last_invoice.id + 1:06d}"
            else:
                self.invoice_number = "INV-000001"
        super().save(*args, **kwargs)
    
    def get_total(self):
        """حساب المجموع الكلي للفاتورة"""
        total = self.items.aggregate(
            total=models.Sum(
                models.F('quantity') * models.F('unit_price'),
                output_field=models.DecimalField(max_digits=12, decimal_places=2)
            )
        )['total']
        return total or Decimal('0')
    
    def get_paid_amount(self):
        """حساب المبلغ المدفوع"""
        total = self.payments.aggregate(
            total=models.Sum('amount')
        )['total']
        return total or Decimal('0')
    
    def get_remaining(self):
        """حساب المبلغ المتبقي"""
        return self.get_total() - self.get_paid_amount()
    
    def update_status(self):
        """تحديث حالة الفاتورة بناءً على الدفعات"""
        if self.status == self.InvoiceStatus.CANCELLED:
            return
        
        if self.status == self.InvoiceStatus.DRAFT:
            return
        
        total = self.get_total()
        paid = self.get_paid_amount()
        
        if paid >= total:
            self.status = self.InvoiceStatus.PAID
        elif paid > 0:
            self.status = self.InvoiceStatus.PARTIAL
        else:
            self.status = self.InvoiceStatus.ISSUED
        
        self.save(update_fields=['status'])
    
    def can_edit(self):
        """هل يمكن تعديل الفاتورة؟"""
        return self.status == self.InvoiceStatus.DRAFT
    
    def can_issue(self):
        """هل يمكن إصدار الفاتورة؟"""
        return self.status == self.InvoiceStatus.DRAFT and self.items.exists()


class InvoiceItem(models.Model):
    """نموذج بند الفاتورة"""
    
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='الفاتورة'
    )
    description = models.CharField(
        max_length=500,
        verbose_name='الوصف'
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='الكمية'
    )
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='سعر الوحدة'
    )
    
    class Meta:
        verbose_name = 'بند فاتورة'
        verbose_name_plural = 'بنود الفاتورة'
    
    def __str__(self):
        return f"{self.description} - {self.get_total()}"
    
    def get_total(self):
        """حساب مجموع البند"""
        return self.quantity * self.unit_price
