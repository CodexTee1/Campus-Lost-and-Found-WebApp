from django.contrib import admin

from .models import Category, Item, ClaimRequest

admin.site.register(Category)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "status", "location", "reported_by", "is_public", "is_verified", "created_at")
    list_filter = ("status", "is_public", "is_verified", "category")
    search_fields = ("name", "description", "location", "reported_by__username")


@admin.register(ClaimRequest)
class ClaimRequestAdmin(admin.ModelAdmin):
    list_display = ("item", "claimed_by", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("item__name", "claimed_by__username", "note")
