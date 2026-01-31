from django.views.generic import CreateView
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from invoices.models import Invoice
from .models import Payment
from .forms import PaymentForm


class PaymentCreateView(CreateView):
    """إضافة دفعة جديدة"""
    model = Payment
    form_class = PaymentForm
    template_name = 'payments/payment_form.html'
    
    def get_invoice(self):
        return get_object_or_404(Invoice, pk=self.kwargs['invoice_id'])
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['invoice'] = self.get_invoice()
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice = self.get_invoice()
        context['invoice'] = invoice
        context['remaining'] = invoice.get_remaining()
        return context
    
    def form_valid(self, form):
        invoice = self.get_invoice()
        
        # التحقق من إمكانية إضافة دفعة
        if invoice.status in [Invoice.InvoiceStatus.DRAFT, Invoice.InvoiceStatus.CANCELLED]:
            messages.error(self.request, 'لا يمكن إضافة دفعة لهذه الفاتورة')
            return self.form_invalid(form)
        
        if invoice.status == Invoice.InvoiceStatus.PAID:
            messages.error(self.request, 'الفاتورة مدفوعة بالكامل')
            return self.form_invalid(form)
        
        form.instance.invoice = invoice
        messages.success(self.request, 'تم إضافة الدفعة بنجاح')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('invoices:detail', kwargs={'pk': self.kwargs['invoice_id']})
