from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.contenttypes.models import ContentType

from main.models import AccountWarehouse, Warehouse

from .models import (Account, AccountData, Buyout, BuyoutCategory, Purchase,
                     PurchaseDeliveryOption, PurchasePhoto)


class AccountAdmin(UserAdmin):
    list_display = ("email", "date_joined")
    search_fields = ("email",)
    ordering = ("-date_joined",)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    list_per_page = 30


admin.site.register(Account, AccountAdmin)


class AccountDataAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "phone", "related_accounts")
    list_filter = (("account", admin.RelatedOnlyFieldListFilter),)
    search_fields = ("first_name", "last_name")
    list_per_page = 30


admin.site.register(AccountData, AccountDataAdmin)


class PurchaseAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "quantity",
        "price",
        "delivery_warehouse_display", 
        "delivery_method",
        "related_accounts",
        "is_deliveried",
        "status",
    )
    list_filter = (("account", admin.RelatedOnlyFieldListFilter),)
    search_fields = ("tracking_number",)
    list_per_page = 30

    def delivery_warehouse_display(self, obj):
        if obj.delivery_warehouse_type:
            if obj.delivery_warehouse_type.model == ContentType.objects.get_for_model(Warehouse).model:
                warehouse = Warehouse.objects.get(id=obj.delivery_warehouse_id)
                return "Склад пользователя: {0}, {1}, {2}".format(
                    warehouse.state, warehouse.city, warehouse.address
                )
            elif obj.delivery_warehouse_type.model == ContentType.objects.get_for_model(AccountWarehouse).model:
                account_warehouse = AccountWarehouse.objects.get(id=obj.delivery_warehouse_id)
                return "Наш склад: {0}, {1}, {2}".format(
                    account_warehouse.state, account_warehouse.city, account_warehouse.address
                )
        return "Неизвестный склад"

    delivery_warehouse_display.short_description = "Куда будет доставлен товар"


admin.site.register(Purchase, PurchaseAdmin)


class PurchasePhotoAdmin(admin.ModelAdmin):
    list_display = ("purchase_name", "photo")
    search_fields = ["purchase__name"]
    list_per_page = 30

    def purchase_name(self, obj):
        return obj.purchase.name

    purchase_name.short_description = "Имя покупки"


admin.site.register(PurchasePhoto, PurchasePhotoAdmin)


class PurchaseDeliveryOptionAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "is_visible")
    list_filter = ("is_visible",)
    search_fields = ("name",)
    ordering = ("is_visible", "name")
    list_per_page = 30


admin.site.register(PurchaseDeliveryOption, PurchaseDeliveryOptionAdmin)


class BuyoutAdmin(admin.ModelAdmin):
    list_display = ("category", "name", "percent")
    list_filter = ("category__name",)
    search_fields = ("name", "category__name")
    list_per_page = 30


admin.site.register(Buyout, BuyoutAdmin)


class BuyoutCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_visible", "total_buyouts")
    list_filter = ("is_visible",)
    search_fields = ("name",)
    list_per_page = 30

    def total_buyouts(self, obj):
        return obj.buyout_set.count()

    total_buyouts.short_description = "Всего вариаций"


admin.site.register(BuyoutCategory, BuyoutCategoryAdmin)
