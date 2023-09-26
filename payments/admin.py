from django.contrib import admin

from .models import Invoice

from django.contrib import admin
from django.utils.html import format_html

from .models import Invoice, Service


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("account", "amount", "status", "created_at", "email_sent_display")
    actions = [
        "send_invoice_email_action",
    ]

    def email_sent_display(self, obj):
        if obj.email_sent:
            return format_html('<span style="color: green;">Да</span>')
        return format_html('<span style="color: red;">Нет</span>')

    email_sent_display.short_description = "Отправлено на email"

    def send_invoice_email_action(self, request, queryset):
        for invoice in queryset:
            invoice.send_invoice_email()
        self.message_user(request, f"Отправлено чеков: {len(queryset)}")

    send_invoice_email_action.short_description = "Отправить выбранные чеки по email"


admin.site.register(Invoice, InvoiceAdmin)


class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "price")
    search_fields = ("name",)
    list_per_page = 30


admin.site.register(Service, ServiceAdmin)
