from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Party
from .forms import PartyForm


class PartyListView(ListView):
    """عرض قائمة الأطراف"""
    model = Party
    template_name = 'parties/party_list.html'
    context_object_name = 'parties'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        party_type = self.request.GET.get('type')
        search = self.request.GET.get('search')
        
        if party_type:
            queryset = queryset.filter(party_type=party_type)
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['party_types'] = Party.PartyType.choices
        context['current_type'] = self.request.GET.get('type', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context


class PartyCreateView(CreateView):
    """إضافة طرف جديد"""
    model = Party
    form_class = PartyForm
    template_name = 'parties/party_form.html'
    success_url = reverse_lazy('parties:list')
    
    def form_valid(self, form):
        messages.success(self.request, 'تم إضافة الطرف بنجاح')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'إضافة طرف جديد'
        context['button_text'] = 'إضافة'
        return context


class PartyUpdateView(UpdateView):
    """تعديل طرف"""
    model = Party
    form_class = PartyForm
    template_name = 'parties/party_form.html'
    success_url = reverse_lazy('parties:list')
    
    def form_valid(self, form):
        messages.success(self.request, 'تم تعديل الطرف بنجاح')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'تعديل: {self.object.name}'
        context['button_text'] = 'حفظ التعديلات'
        return context


class PartyDetailView(DetailView):
    """عرض تفاصيل طرف"""
    model = Party
    template_name = 'parties/party_detail.html'
    context_object_name = 'party'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from ledger.models import LedgerEntry
        context['ledger_entries'] = LedgerEntry.objects.filter(
            party=self.object
        ).order_by('-date')[:20]
        context['balance'] = self.object.get_balance()
        return context
