from django.views.generic import DetailView, TemplateView
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from decimal import Decimal
from datetime import date, timedelta
from parties.models import Party
from invoices.models import Invoice
from ledger.models import LedgerEntry


class PartyReportView(DetailView):
    """تقرير رصيد طرف"""
    model = Party
    template_name = 'reports/party_report.html'
    context_object_name = 'party'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        party = self.object
        
        # إجمالي الفواتير
        sale_invoices = Invoice.objects.filter(
            party=party,
            invoice_type=Invoice.InvoiceType.SALE,
            status__in=[Invoice.InvoiceStatus.ISSUED, Invoice.InvoiceStatus.PAID, Invoice.InvoiceStatus.PARTIAL]
        )
        purchase_invoices = Invoice.objects.filter(
            party=party,
            invoice_type=Invoice.InvoiceType.PURCHASE,
            status__in=[Invoice.InvoiceStatus.ISSUED, Invoice.InvoiceStatus.PAID, Invoice.InvoiceStatus.PARTIAL]
        )
        
        # حساب إجماليات الفواتير
        context['total_sales'] = sum(inv.get_total() for inv in sale_invoices)
        context['total_purchases'] = sum(inv.get_total() for inv in purchase_invoices)
        
        # إجمالي الدفعات
        from payments.models import Payment
        context['total_payments'] = Payment.objects.filter(
            invoice__party=party
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # الرصيد الحالي
        balance = party.get_balance()
        context['balance'] = balance
        
        # فئات التنسيق
        if balance > 0:
            context['balance_class'] = 'bg-debit'
            context['balance_text'] = 'له علينا (مدين)'
        elif balance < 0:
            context['balance_class'] = 'bg-credit'
            context['balance_text'] = 'لنا عليه (دائن)'
        else:
            context['balance_class'] = 'bg-neutral'
            context['balance_text'] = 'الرصيد الحالي'
        
        # سجل الحركات
        context['ledger_entries'] = LedgerEntry.objects.filter(
            party=party
        ).select_related('invoice', 'payment').order_by('-date', '-created_at')
        
        # الفواتير الأخيرة
        context['recent_invoices'] = Invoice.objects.filter(
            party=party
        ).order_by('-created_at')[:10]
        
        return context


class SummaryReportView(TemplateView):
    """تقرير ملخص الفترة"""
    template_name = 'reports/summary_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # فلترة التاريخ
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        # الافتراضي: آخر 30 يوم
        if not date_to:
            date_to = date.today()
        else:
            date_to = date.fromisoformat(date_to)
        
        if not date_from:
            date_from = date_to - timedelta(days=30)
        else:
            date_from = date.fromisoformat(date_from)
        
        context['date_from'] = date_from
        context['date_to'] = date_to
        
        # الفواتير في الفترة
        invoices = Invoice.objects.filter(
            issue_date__gte=date_from,
            issue_date__lte=date_to,
            status__in=[Invoice.InvoiceStatus.ISSUED, Invoice.InvoiceStatus.PAID, Invoice.InvoiceStatus.PARTIAL]
        )
        
        # حساب الإجماليات
        sale_invoices = [inv for inv in invoices if inv.invoice_type == Invoice.InvoiceType.SALE]
        purchase_invoices = [inv for inv in invoices if inv.invoice_type == Invoice.InvoiceType.PURCHASE]
        
        context['total_sales'] = sum(inv.get_total() for inv in sale_invoices)
        context['total_purchases'] = sum(inv.get_total() for inv in purchase_invoices)
        net_balance = context['total_sales'] - context['total_purchases']
        context['net_balance'] = net_balance
        
        if net_balance >= 0:
            context['net_balance_class'] = 'bg-credit' # أخضر للربح
            context['net_balance_label'] = 'ربح'
        else:
            context['net_balance_class'] = 'bg-debit' # أحمر للخسارة
            context['net_balance_label'] = 'خسارة'
        
        context['sales_count'] = len(sale_invoices)
        context['purchases_count'] = len(purchase_invoices)
        
        # الدفعات في الفترة
        from payments.models import Payment
        payments = Payment.objects.filter(
            payment_date__gte=date_from,
            payment_date__lte=date_to
        )
        context['total_payments'] = payments.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        context['payments_count'] = payments.count()
        
        # قيود الأستاذ في الفترة
        ledger_entries = LedgerEntry.objects.filter(
            date__gte=date_from,
            date__lte=date_to
        )
        
        context['total_debit'] = ledger_entries.filter(
            entry_type=LedgerEntry.EntryType.DEBIT
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        context['total_credit'] = ledger_entries.filter(
            entry_type=LedgerEntry.EntryType.CREDIT
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # أرصدة الأطراف
        parties_with_balance = []
        for party in Party.objects.all():
            balance = party.get_balance()
            if balance != 0:
                parties_with_balance.append({
                    'party': party,
                    'balance': balance,
                    'balance_type': 'مدين' if balance > 0 else 'دائن'
                })
        
        context['parties_with_balance'] = sorted(
            parties_with_balance,
            key=lambda x: abs(x['balance']),
            reverse=True
        )
        
        return context
