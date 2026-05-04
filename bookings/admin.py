from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['space', 'tenant', 'date_from', 'date_to', 'status', 'total_price', 'created_at']
    list_filter = ['status']
    search_fields = ['space__title', 'tenant__username']
    raw_id_fields = ['space', 'tenant']
