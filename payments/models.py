from uuid import uuid4

from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

from accounts.models import Account

INVOICE_CHOICES = (
    ("ACTIVE", "active"),
    ("PAID", "paid"),
    ("EXPIRED", "expired"),
)


class Invoice(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    invoice_id = models.BigIntegerField(verbose_name="Идентификатор транзакции", null=True, blank=True)
    slug = models.CharField(verbose_name="SLUG", max_length=1024, default=uuid4)
    asset = models.CharField(max_length=10, null=True, blank=True)
    amount = models.DecimalField(verbose_name="Сумма", max_digits=12, decimal_places=2)
    pay_url = models.CharField(verbose_name="Ссылка на оплату", max_length=1024,null=True, blank=True)
    status = models.CharField(max_length=15, choices=INVOICE_CHOICES, default="ACTIVE")
    created_at = models.DateTimeField(verbose_name="Дата создания оплаты", auto_now_add=True)
    email_sent = models.BooleanField(default=False)

    def send_invoice_email(self):
        if not self.email_sent:
            subject = 'Ваш чек'
            context = {'invoice': self}
            html_message = render_to_string('payments/invoice_email_template.html', context)
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

    class Meta:
        ordering = ['-created_at']
        verbose_name="Чек"
        verbose_name_plural="Чеки"

    def __str__(self) -> str:
        return f"{self.account.email} -> ${self.amount}"



