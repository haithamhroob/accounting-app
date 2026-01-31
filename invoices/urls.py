from django.urls import path
from . import views

app_name = 'invoices'

urlpatterns = [
    path('', views.InvoiceListView.as_view(), name='list'),
    path('add/', views.InvoiceCreateView.as_view(), name='create'),
    path('<int:pk>/', views.InvoiceDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.InvoiceUpdateView.as_view(), name='update'),
    path('<int:pk>/issue/', views.InvoiceIssueView.as_view(), name='issue'),
    path('<int:pk>/cancel/', views.InvoiceCancelView.as_view(), name='cancel'),
]
