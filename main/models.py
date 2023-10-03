import datetime

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

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
        return f"Склад: {self.state}, {self.city}, {self.address}"


class WarehouseShop(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    warehouse = GenericForeignKey("content_type", "object_id")
    name = models.CharField(verbose_name="Имя магазина", max_length=255)
    quantity = models.BigIntegerField(
        verbose_name="Количество заказов на адрес", default=0
    )
    image = models.ImageField(verbose_name="Путь до фото", max_length=2048)

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        verbose_name = "Магазин склада"
        verbose_name_plural = "Магазины склада"


class AccountWarehouse(models.Model):
    address = models.CharField(verbose_name="Улица", max_length=255)
    city = models.CharField(verbose_name="Город", max_length=255)
    state = models.CharField(verbose_name="Штат", max_length=255)
    zip = models.CharField(verbose_name="Почтовый индекс", max_length=255)
    phone = models.CharField(verbose_name="Номер телефона", max_length=255)
    account = models.ForeignKey(User, on_delete=models.CASCADE)

    is_opened = models.BooleanField(verbose_name="Открыт", default=False)
    opened_date = models.DateTimeField(verbose_name="Дата открытия склада", null=True, blank=True)

    def is_user_access(self):
        if self.opened_date is None:
            return False 
        now = timezone.now()
        time_difference =  now - self.opened_date
        if time_difference.days >= 30:
            return False 
        return True
    
    def pretty_end_time(self):
        if self.opened_date:
            now = timezone.now()
            time_difference =  now - self.opened_date
            days = 30 - time_difference.days

            return _("Срок действия заканчивается через {0} {1}").format(
                days,
                _("день" if days == 1 else "дня" if 1 < days < 5 else "дней")
            )
        else:
            return _("Дата открытия не установлена")

    class Meta:
        verbose_name = "Склад"
        verbose_name_plural = "Склады пользователей"


    def __str__(self) -> str:
        return f"{self.state}, {self.city}, {self.address}"
