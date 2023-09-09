from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import Warehouse, AccountWarehouse, WarehouseShop

class WarehouseShopInline(GenericTabularInline):
    model = WarehouseShop
    extra = 0

class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("state", "city", "address")
    search_fields = ("state", "city", "address")
    inlines = [WarehouseShopInline]

class AccountWarehouseAdmin(admin.ModelAdmin):
    list_display = ("account", "state", "city", "address")
    search_fields = ("account__username", "state", "city", "address")

class WarehouseShopAdmin(admin.ModelAdmin):
    list_display = ("name", "get_warehouse", "quantity", "image")
    list_filter = ("content_type",)
    search_fields = ("name", "warehouse__account__username", "warehouse__state", "warehouse__city", "warehouse__address")

    def get_warehouse(self, obj):
        if obj.warehouse:
            return f"{obj.warehouse.state}, {obj.warehouse.city}, {obj.warehouse.address}"
        return "N/A"

    get_warehouse.short_description = "Склад"

admin.site.register(Warehouse, WarehouseAdmin)
admin.site.register(AccountWarehouse, AccountWarehouseAdmin)
admin.site.register(WarehouseShop, WarehouseShopAdmin)