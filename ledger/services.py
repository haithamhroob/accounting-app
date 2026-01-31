"""
خدمات دفتر الأستاذ
تنفيذ القواعد المحاسبية:
- إصدار فاتورة بيع => حركة مدينة على العميل
- إصدار فاتورة شراء => حركة دائنة على المورد
- دفعة من عميل => حركة دائنة
- دفعة لمورد => حركة مدينة
"""

from .models import LedgerEntry


def create_invoice_entry(invoice):
    """
    إنشاء قيد دفتر الأستاذ عند إصدار فاتورة
    
    فاتورة بيع للعميل = مدين (له علينا مبلغ)
    فاتورة شراء من مورد = دائن (لنا عليه مبلغ)
    """
    from invoices.models import Invoice
    
    total = invoice.get_total()
    if total <= 0:
        return None
    
    # تحديد نوع الحركة
    if invoice.invoice_type == Invoice.InvoiceType.SALE:
        # فاتورة بيع: العميل مدين لنا
        entry_type = LedgerEntry.EntryType.DEBIT
        description = f"فاتورة بيع رقم {invoice.invoice_number}"
    else:
        # فاتورة شراء: نحن مدينون للمورد
        entry_type = LedgerEntry.EntryType.CREDIT
        description = f"فاتورة شراء رقم {invoice.invoice_number}"
    
    entry = LedgerEntry.objects.create(
        party=invoice.party,
        invoice=invoice,
        entry_type=entry_type,
        amount=total,
        date=invoice.issue_date,
        description=description
    )
    
    return entry


def create_payment_entry(payment):
    """
    إنشاء قيد دفتر الأستاذ عند تسجيل دفعة
    
    دفعة من عميل = دائن (سدد جزء من الدين)
    دفعة لمورد = مدين (أنقصنا من دينه علينا)
    """
    from invoices.models import Invoice
    
    invoice = payment.invoice
    
    # تحديد نوع الحركة (عكس الفاتورة)
    if invoice.invoice_type == Invoice.InvoiceType.SALE:
        # دفعة من عميل: تخفيض الدين المدين
        entry_type = LedgerEntry.EntryType.CREDIT
        description = f"دفعة على فاتورة {invoice.invoice_number}"
    else:
        # دفعة لمورد: تخفيض الدين الدائن
        entry_type = LedgerEntry.EntryType.DEBIT
        description = f"دفعة لفاتورة {invoice.invoice_number}"
    
    entry = LedgerEntry.objects.create(
        party=invoice.party,
        invoice=invoice,
        payment=payment,
        entry_type=entry_type,
        amount=payment.amount,
        date=payment.payment_date,
        description=description
    )
    
    return entry


def get_party_balance(party):
    """
    حساب رصيد الطرف
    الرصيد = مجموع المدين - مجموع الدائن
    
    إذا كان موجب = له علينا (عميل لم يسدد)
    إذا كان سالب = لنا عليه (مورد لم نسدد له)
    """
    from django.db.models import Sum
    from decimal import Decimal
    
    entries = LedgerEntry.objects.filter(party=party)
    
    debit = entries.filter(
        entry_type=LedgerEntry.EntryType.DEBIT
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    credit = entries.filter(
        entry_type=LedgerEntry.EntryType.CREDIT
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    return debit - credit
