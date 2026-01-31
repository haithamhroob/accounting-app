from django.views.generic import ListView, CreateView, UpdateView, DetailView, View
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from .models import Invoice
from .forms import InvoiceForm, InvoiceItemFormSet


class InvoiceListView(ListView):
    """عرض قائمة الفواتير"""
    model = Invoice
    template_name = 'invoices/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('party')
        invoice_type = self.request.GET.get('type')
        status = self.request.GET.get('status')
        search = self.request.GET.get('search')
        
        if invoice_type:
            queryset = queryset.filter(invoice_type=invoice_type)
        if status:
            queryset = queryset.filter(status=status)
        if search:
            queryset = queryset.filter(
                invoice_number__icontains=search
            ) | queryset.filter(
                party__name__icontains=search
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoice_types'] = Invoice.InvoiceType.choices
        context['invoice_statuses'] = Invoice.InvoiceStatus.choices
        context['current_type'] = self.request.GET.get('type', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context


class InvoiceCreateView(CreateView):
    """إنشاء فاتورة جديدة"""
    model = Invoice
    form_class = InvoiceForm
    template_name = 'invoices/invoice_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'إنشاء فاتورة جديدة'
        context['button_text'] = 'إنشاء الفاتورة'
        
        if self.request.POST:
            context['items_formset'] = InvoiceItemFormSet(self.request.POST)
        else:
            context['items_formset'] = InvoiceItemFormSet()
        
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        items_formset = context['items_formset']
        
        with transaction.atomic():
            self.object = form.save()
            
            if items_formset.is_valid():
                items_formset.instance = self.object
                items_formset.save()
                messages.success(self.request, 'تم إنشاء الفاتورة بنجاح')
                return redirect(self.object.get_absolute_url())
            else:
                return self.form_invalid(form)
    
    def get_success_url(self):
        return reverse('invoices:detail', kwargs={'pk': self.object.pk})


class InvoiceUpdateView(UpdateView):
    """تعديل فاتورة"""
    model = Invoice
    form_class = InvoiceForm
    template_name = 'invoices/invoice_form.html'
    
    def get_queryset(self):
        # فقط المسودات يمكن تعديلها
        return super().get_queryset().filter(status=Invoice.InvoiceStatus.DRAFT)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'تعديل الفاتورة: {self.object.invoice_number}'
        context['button_text'] = 'حفظ التعديلات'
        
        if self.request.POST:
            context['items_formset'] = InvoiceItemFormSet(
                self.request.POST, instance=self.object
            )
        else:
            context['items_formset'] = InvoiceItemFormSet(instance=self.object)
        
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        items_formset = context['items_formset']
        
        with transaction.atomic():
            self.object = form.save()
            
            if items_formset.is_valid():
                items_formset.save()
                messages.success(self.request, 'تم تعديل الفاتورة بنجاح')
                return redirect(self.object.get_absolute_url())
            else:
                return self.form_invalid(form)


class InvoiceDetailView(DetailView):
    """عرض تفاصيل فاتورة"""
    model = Invoice
    template_name = 'invoices/invoice_detail.html'
    context_object_name = 'invoice'
    
    def get_queryset(self):
        return super().get_queryset().select_related('party').prefetch_related('items', 'payments')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total'] = self.object.get_total()
        context['paid'] = self.object.get_paid_amount()
        context['remaining'] = self.object.get_remaining()
        return context


class InvoiceIssueView(View):
    """إصدار الفاتورة"""
    
    def post(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)
        
        if not invoice.can_issue():
            messages.error(request, 'لا يمكن إصدار هذه الفاتورة')
            return redirect(invoice.get_absolute_url())
        
        with transaction.atomic():
            invoice.status = Invoice.InvoiceStatus.ISSUED
            invoice.save(update_fields=['status'])
            
            # إنشاء قيد دفتر الأستاذ
            from ledger.services import create_invoice_entry
            create_invoice_entry(invoice)
            
            messages.success(request, 'تم إصدار الفاتورة بنجاح')
        
        return redirect(invoice.get_absolute_url())


class InvoiceCancelView(View):
    """إلغاء الفاتورة"""
    
    def post(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)
        
        if invoice.status == Invoice.InvoiceStatus.CANCELLED:
            messages.error(request, 'الفاتورة ملغاة بالفعل')
            return redirect(invoice.get_absolute_url())
        
        if invoice.get_paid_amount() > 0:
            messages.error(request, 'لا يمكن إلغاء فاتورة لها دفعات')
            return redirect(invoice.get_absolute_url())
        
        with transaction.atomic():
            # حذف قيود الأستاذ إن وجدت
            from ledger.models import LedgerEntry
            LedgerEntry.objects.filter(invoice=invoice).delete()
            
            invoice.status = Invoice.InvoiceStatus.CANCELLED
            invoice.save(update_fields=['status'])
            
            messages.success(request, 'تم إلغاء الفاتورة')
        
        return redirect(invoice.get_absolute_url())
