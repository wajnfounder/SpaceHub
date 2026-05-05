from django.contrib import admin
from .models import Space, SpaceImage, SpaceAmenity, AdditionalService


class SpaceImageInline(admin.TabularInline):
    model = SpaceImage
    extra = 1


class SpaceAmenityInline(admin.TabularInline):
    model = SpaceAmenity
    extra = 2


class AdditionalServiceInline(admin.TabularInline):
    model = AdditionalService
    extra = 1


@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    list_display  = ['title', 'owner', 'space_type', 'city', 'status', 'price_per_day', 'created_at']
    list_filter   = ['space_type', 'status', 'city', 'rental_type']
    search_fields = ['title', 'owner__username', 'address']
    inlines       = [SpaceImageInline, SpaceAmenityInline, AdditionalServiceInline]
    raw_id_fields = ['owner']


@admin.register(SpaceImage)
class SpaceImageAdmin(admin.ModelAdmin):
    list_display = ['space', 'is_main']
    list_filter  = ['is_main']


@admin.register(SpaceAmenity)
class SpaceAmenityAdmin(admin.ModelAdmin):
    list_display  = ['space', 'name']
    list_filter   = ['name']


@admin.register(AdditionalService)
class AdditionalServiceAdmin(admin.ModelAdmin):
    list_display  = ['space', 'service_type', 'price']
    list_filter   = ['service_type']
