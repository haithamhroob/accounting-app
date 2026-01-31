from django.urls import path
from . import views

app_name = 'parties'

urlpatterns = [
    path('', views.PartyListView.as_view(), name='list'),
    path('add/', views.PartyCreateView.as_view(), name='create'),
    path('<int:pk>/', views.PartyDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.PartyUpdateView.as_view(), name='update'),
]
