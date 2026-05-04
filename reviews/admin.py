from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'space', 'rating', 'created_at']
    list_filter = ['rating']
    search_fields = ['user__username', 'space__title', 'comment']
    raw_id_fields = ['space', 'user']
