import datetime
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


def now_plus_month():
    return datetime.datetime.now() + datetime.timedelta(days=28)


class Warehouse(models.Model):
    address = models.CharField(verbose_name="Улица", max_length=255)
    city = models.CharField(verbose_name="Город", max_length=255)
    state = models.CharField(verbose_name="Штат", max_length=255)
    zip = models.CharField(verbose_name="Почтовый индекс", max_length=255)
    phone = models.CharField(verbose_name="Номер телефона", max_length=255)

    opened = models.DateTimeField(
        verbose_name="Склад открыт", default=datetime.datetime.now
    )
    closed = models.DateTimeField(
        verbose_name="Склад будет закрыт", default=now_plus_month
    )

    class Meta:
        verbose_name = "Склад"
        verbose_name_plural = "Склады"

    def __str__(self) -> str:
        return f"{self.opened} -> {self.state} -> {self.city} -> {self.address}"


class AccountWarehouse(Warehouse):
    account = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Склад"
        verbose_name_plural = "Склады пользователей"

    def __str__(self) -> str:
        return f"{self.account} -> {self.state} -> {self.city} -> {self.address}"
