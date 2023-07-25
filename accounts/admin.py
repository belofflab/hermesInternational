from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Account, Visits, Purchase


class AccountAdmin(UserAdmin):
    list_display = ("email", "date_joined")
    search_fields = ("email",)
    ordering = ("email",)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Account, AccountAdmin)

admin.site.register(Visits)

admin.site.register(Purchase)