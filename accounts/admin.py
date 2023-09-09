from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

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
        "related_accounts",
        "is_deliveried",
        "status",
    )
    list_filter = (("account", admin.RelatedOnlyFieldListFilter),)
    search_fields = ("tracking_number",)
    list_per_page = 30


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
