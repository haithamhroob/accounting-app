from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('add/<int:invoice_id>/', views.PaymentCreateView.as_view(), name='create'),
]
