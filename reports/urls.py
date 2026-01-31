from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('party/<int:pk>/', views.PartyReportView.as_view(), name='party'),
    path('summary/', views.SummaryReportView.as_view(), name='summary'),
]
