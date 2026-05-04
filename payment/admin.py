from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display  = ['pk', 'booking', 'user', 'method', 'status', 'amount', 'created_at']
    list_filter   = ['status', 'method']
    search_fields = ['user__username', 'reference']
    readonly_fields = ['reference', 'created_at']
