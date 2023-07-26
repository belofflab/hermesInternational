from django.db import models
from accounts.models import Account


INVOICE_CHOICES = (
    ("ACTIVE", "active"),
    ("PAID", "paid"),
    ("EXPIRED", "expired"),
)


class Invoice(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    invoice_id = models.BigIntegerField(verbose_name="Идентификатор транзакции")
    asset = models.CharField(max_length=10)
    amount = models.DecimalField(verbose_name="Сумма", max_digits=12, decimal_places=2)
    pay_url = models.CharField(verbose_name="Ссылка на оплату", max_length=1024)
    status = models.CharField(max_length=15, choices=INVOICE_CHOICES, default="ACTIVE")
    created_at = models.DateTimeField(verbose_name="Дата создания оплаты")

    class Meta:
        ordering = ['-created_at']
        verbose_name="Чек"
        verbose_name_plural="Чеки"

    def __str__(self) -> str:
        return f"{self.account.email} -> ${self.amount}"



