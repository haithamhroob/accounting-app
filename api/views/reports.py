"""
Report Views
عرض التقارير
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from decimal import Decimal
from datetime import date, timedelta
from drf_spectacular.utils import extend_schema, OpenApiParameter

from parties.models import Party
from invoices.models import Invoice
from payments.models import Payment
from ledger.models import LedgerEntry
from api.permissions import RoleBasedPermission


class SummaryReportView(APIView):
    """
    Summary report for a date range
    تقرير ملخص لفترة زمنية
    """
    permission_classes = [RoleBasedPermission]
    
    @extend_schema(
        summary="تقرير ملخص الفترة",
        description="الحصول على ملخص للنشاط المالي خلال فترة زمنية",
        tags=["التقارير - Reports"],
        parameters=[
            OpenApiParameter(name='date_from', type=str, description='تاريخ البداية (YYYY-MM-DD)'),
            OpenApiParameter(name='date_to', type=str, description='تاريخ النهاية (YYYY-MM-DD)'),
        ],
        responses={200: {
            "type": "object",
            "properties": {
                "period": {"type": "object"},
                "invoices": {"type": "object"},
                "payments": {"type": "object"},
                "ledger": {"type": "object"},
                "parties_with_balance": {"type": "array"},
            }
        }}
    )
    def get(self, request):
        # Parse date range
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        if not date_to:
            date_to = date.today()
        else:
            date_to = date.fromisoformat(date_to)
        
        if not date_from:
            date_from = date_to - timedelta(days=30)
        else:
            date_from = date.fromisoformat(date_from)
        
        # Get invoices in period
        invoices = Invoice.objects.filter(
            issue_date__gte=date_from,
            issue_date__lte=date_to,
            status__in=['issued', 'paid', 'partial']
        )
        
        sale_invoices = [inv for inv in invoices if inv.invoice_type == 'sale']
        purchase_invoices = [inv for inv in invoices if inv.invoice_type == 'purchase']
        
        total_sales = sum(inv.get_total() for inv in sale_invoices)
        total_purchases = sum(inv.get_total() for inv in purchase_invoices)
        
        # Get payments in period
        payments = Payment.objects.filter(
            payment_date__gte=date_from,
            payment_date__lte=date_to
        )
        total_payments = payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Get ledger entries
        ledger_entries = LedgerEntry.objects.filter(
            date__gte=date_from,
            date__lte=date_to
        )
        total_debit = ledger_entries.filter(entry_type='debit').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        total_credit = ledger_entries.filter(entry_type='credit').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        
        # Get parties with balance
        parties_with_balance = []
        for party in Party.objects.all():
            balance = party.get_balance()
            if balance != 0:
                parties_with_balance.append({
                    'id': party.id,
                    'name': party.name,
                    'party_type': party.party_type,
                    'balance': str(balance),
                    'balance_type': 'مدين' if balance > 0 else 'دائن'
                })
        
        parties_with_balance.sort(key=lambda x: abs(Decimal(x['balance'])), reverse=True)
        
        return Response({
            'period': {
                'from': str(date_from),
                'to': str(date_to)
            },
            'invoices': {
                'total_sales': str(total_sales),
                'total_purchases': str(total_purchases),
                'net_balance': str(total_sales - total_purchases),
                'sales_count': len(sale_invoices),
                'purchases_count': len(purchase_invoices)
            },
            'payments': {
                'total': str(total_payments),
                'count': payments.count()
            },
            'ledger': {
                'total_debit': str(total_debit),
                'total_credit': str(total_credit)
            },
            'parties_with_balance': parties_with_balance[:20]  # Top 20
        })


class PartyReportView(APIView):
    """
    Detailed report for a specific party
    تقرير مفصل لطرف محدد
    """
    permission_classes = [RoleBasedPermission]
    
    @extend_schema(
        summary="تقرير طرف",
        description="الحصول على تقرير مفصل لعميل أو مورد محدد",
        tags=["التقارير - Reports"],
        responses={200: {
            "type": "object",
            "properties": {
                "party": {"type": "object"},
                "invoices": {"type": "object"},
                "payments": {"type": "object"},
                "balance": {"type": "object"},
                "recent_ledger_entries": {"type": "array"},
            }
        }}
    )
    def get(self, request, pk):
        try:
            party = Party.objects.get(pk=pk)
        except Party.DoesNotExist:
            return Response({'error': 'الطرف غير موجود'}, status=404)
        
        # Get invoices
        sale_invoices = Invoice.objects.filter(
            party=party,
            invoice_type='sale',
            status__in=['issued', 'paid', 'partial']
        )
        purchase_invoices = Invoice.objects.filter(
            party=party,
            invoice_type='purchase',
            status__in=['issued', 'paid', 'partial']
        )
        
        total_sales = sum(inv.get_total() for inv in sale_invoices)
        total_purchases = sum(inv.get_total() for inv in purchase_invoices)
        
        # Get payments
        total_payments = Payment.objects.filter(
            invoice__party=party
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Get balance
        balance = party.get_balance()
        
        # Get recent ledger entries
        ledger_entries = LedgerEntry.objects.filter(
            party=party
        ).select_related('invoice', 'payment').order_by('-date', '-created_at')[:20]
        
        entries_data = [{
            'id': entry.id,
            'entry_type': entry.entry_type,
            'entry_type_display': entry.get_entry_type_display(),
            'amount': str(entry.amount),
            'date': str(entry.date),
            'description': entry.description,
            'invoice_number': entry.invoice.invoice_number if entry.invoice else None
        } for entry in ledger_entries]
        
        return Response({
            'party': {
                'id': party.id,
                'name': party.name,
                'party_type': party.party_type,
                'party_type_display': party.get_party_type_display(),
                'phone': party.phone,
                'email': party.email
            },
            'invoices': {
                'total_sales': str(total_sales),
                'total_purchases': str(total_purchases),
                'sales_count': sale_invoices.count(),
                'purchases_count': purchase_invoices.count()
            },
            'payments': {
                'total': str(total_payments)
            },
            'balance': {
                'value': str(balance),
                'display': party.get_balance_display()
            },
            'recent_ledger_entries': entries_data
        })
