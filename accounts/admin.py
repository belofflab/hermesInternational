from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (Account, AccountData, Purchase, PurchasePhoto,
                     PurchaseDeliveryOption, AccountNotifySettings, Visits, Buyout, BuyoutCategory)


class AccountAdmin(UserAdmin):
    list_display = ("email", "date_joined")
    search_fields = ("email",)
    ordering = ("email",)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Account, AccountAdmin)
admin.site.register(AccountData)

admin.site.register(Visits)

admin.site.register(Purchase)
admin.site.register(PurchasePhoto)
admin.site.register(PurchaseDeliveryOption)

admin.site.register(AccountNotifySettings)


admin.site.register(Buyout)
admin.site.register(BuyoutCategory)