from uuid import uuid4

from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.translation import gettext as _

from accounts.models import Account
from payments.services.crypto import Crypto

crypto = Crypto(token=settings.CRYPTO_BOT_TOKEN)

INVOICE_CHOICES = (
    ("ACTIVE", "active"),
    ("PAID", "paid"),
    ("EXPIRED", "expired"),
)


class Service(models.Model):
    name = models.CharField(verbose_name="Наименование услуги", max_length=255)
    price = models.DecimalField(
        verbose_name="Цена ($)", max_digits=12, decimal_places=2
    )

    def __str__(self) -> str:
        return f"{self.name} (${self.price})"
    
    class Meta:
        verbose_name = "Услугу"
        verbose_name_plural = "Услуги"


class Invoice(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    invoice_id = models.BigIntegerField(
        verbose_name="Идентификатор транзакции", null=True, blank=True
    )
    service = models.ForeignKey(
        Service, verbose_name="Наименование услуги", on_delete=models.CASCADE, blank=True, null=True
    )
    slug = models.CharField(verbose_name="SLUG", max_length=1024, default=uuid4)
    asset = models.CharField(max_length=10, null=True, blank=True)
    amount = models.DecimalField(verbose_name="Сумма", max_digits=12, decimal_places=2)
    pay_url = models.CharField(
        verbose_name="Ссылка на оплату", max_length=1024, null=True, blank=True
    )
    status = models.CharField(max_length=15, choices=INVOICE_CHOICES, default="ACTIVE")
    created_at = models.DateTimeField(
        verbose_name="Дата создания оплаты", auto_now_add=True
    )
    email_sent = models.BooleanField(default=False)

    def send_invoice_email(self):
        new_invoice = {}
        if self.pay_url is None and self.invoice_id is None:
            new_invoice = self.create_invoice(amount=str(self.service.price) if self.service else self.amount)
        if not self.email_sent:
            subject = _("Ваш чек на оплату ") + f"«{self.service.name.lower()}» ${self.amount}"
            context = {"pay_url": new_invoice, "service": self.service.name}
            html_message = render_to_string(
                "payments/invoice_email_template.html", context
            )
            plain_message = strip_tags(html_message)
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = self.account.email

            send_mail(
                subject,
                plain_message,
                from_email,
                [to_email],
                html_message=html_message,
            )
            self.email_sent = True
            self.save()

    def create_invoice(self, amount: str):
        receipt = crypto.createInvoice("USDT", amount=amount)
        if receipt.get("ok"):
            result = receipt.get("result")
            self.invoice_id = result.get("invoice_id")
            self.asset = result.get("asset")
            self.pay_url = result.get("pay_url")
            self.status = result.get("status")
            self.created_at = result.get("created_at")

            self.save()

            invoice_detail_url = reverse(
                "payments:invoice_detail", kwargs={"invoice_slug": self.slug}
            )
            return "https://hermesinternational.ru" + invoice_detail_url
        return ""

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Чек"
        verbose_name_plural = "Чеки"

    def __str__(self) -> str:
        return f"{self.account.email} -> ${self.amount}"
