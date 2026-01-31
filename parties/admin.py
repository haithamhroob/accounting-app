from django.contrib import admin
from .models import Party


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ['name', 'party_type', 'phone', 'email', 'created_at']
    list_filter = ['party_type', 'created_at']
    search_fields = ['name', 'phone', 'email']
    ordering = ['-created_at']
