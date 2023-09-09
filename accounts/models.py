from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.deconstruct import deconstructible


PURCHASE_STATUS_CHOICES = (
    ("BUYOUT", "buyout"),
    ("FORWARDING", "forwarding"),
    ("ACCEPTANCE", "acceptance"),
)


class PurchaseDeliveryOption(models.Model):
    """Добавочные функции отправки посылки"""

    name = models.CharField(verbose_name="Наименование", max_length=255)
    price = models.DecimalField(
        verbose_name="Стоимость", max_digits=12, decimal_places=2
    )
    is_visible = models.BooleanField(verbose_name="Доступна", default=True)

    class Meta:
        verbose_name = "Доставочная опция"
        verbose_name_plural = "Доставочные опции"

    def __str__(self) -> str:
        return f"({'Включена' if self.is_visible else 'Отключена'}) {self.name} ${self.price}"


class Purchase(models.Model):
    """Модель покупки"""

    name = models.CharField(verbose_name="Наименование товара ", max_length=255)
    link = models.CharField(verbose_name="Ссылка на товар", max_length=2048)
    quantity = models.IntegerField(verbose_name="Количество товара")
    address = models.ForeignKey(
        "AccountData",
        verbose_name="Куда нужно переслать",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    delivery_method = models.CharField(
        verbose_name="Метод доставки", max_length=255, null=True, blank=True
    )
    is_deliveried = models.BooleanField(verbose_name="Доставлена", default=False)
    options = models.ManyToManyField(
        to=PurchaseDeliveryOption, verbose_name="Доступные опции доставки", blank=True
    )
    price = models.DecimalField(
        verbose_name="Цена товара", max_digits=12, decimal_places=2
    )
    tracking_number = models.CharField(
        verbose_name="Трек номер", max_length=255, null=True
    )
    status = models.CharField(
        verbose_name="Текущий статус:",
        max_length=255,
        choices=PURCHASE_STATUS_CHOICES,
        default="ACCEPTANCE",
    )
    created = models.DateTimeField(auto_now_add=True)

    def search_related_accounts(self, query):
        return Account.objects.filter(purchases=self, email__icontains=query)

    def related_accounts(self):
        return ", ".join([account.email for account in self.account_set.all()])

    related_accounts.short_description = "Связанные аккаунты"

    class Meta:
        verbose_name = "покупку"
        verbose_name_plural = "покупки"
        ordering = ["-created"]

    def __str__(self) -> str:
        return f"{self.name}_{self.quantity}_${self.price}"


class PurchasePhoto(models.Model):
    """Модель для фотографий покупок"""

    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name="photos",
        verbose_name="Покупка",
    )
    photo = models.ImageField(
        verbose_name="Фотография",
        upload_to="purchase_photos/",
    )

    class Meta:
        verbose_name = "Фотография покупки"
        verbose_name_plural = "Фотографии покупок"

    def __str__(self):
        return f"Фото для {self.purchase.name}"


class AccountManager(BaseUserManager):
    """Менеджер кастомной модели пользователя"""

    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Ползователи должны иметь адрес электронной почты")

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.model(email=self.normalize_email(email), password=password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save(using=self._db)
        return user


class AccountData(models.Model):
    """Информация о пользователе для доставок"""

    first_name = models.CharField(
        verbose_name="Имя", max_length=255, blank=True, null=True
    )
    last_name = models.CharField(
        verbose_name="Фамилия", max_length=255, blank=True, null=True
    )
    phone = models.CharField(verbose_name="Номер телефона", max_length=255, null=True)
    city = models.CharField(verbose_name="Город", max_length=255)
    street = models.CharField(verbose_name="Улица", max_length=255)
    state = models.CharField(verbose_name="Штат", max_length=255)
    postal_code = models.CharField(verbose_name="Почтовый индекс", max_length=255)
    country = models.CharField(verbose_name="Страна", max_length=255)

    def search_related_accounts(self, query):
        return Account.objects.filter(purchases=self, email__icontains=query)

    def related_accounts(self):
        return ", ".join([account.email for account in self.account_set.all()])

    related_accounts.short_description = "Связанные аккаунты"

    class Meta:
        verbose_name = "Доставочный адрес"
        verbose_name_plural = "Доставочные адреса"

    def __str__(self) -> str:
        return f"{self.country} -> {self.city} -> {self.street}"


@deconstructible
class UserImagePath:
    def __init__(self, sub_path):
        self.sub_path = sub_path

    def __call__(self, instance, filename):
        # filename will be the original uploaded filename
        # Generate a unique filename based on user's id and original file extension
        ext = filename.split(".")[-1]
        new_filename = f"user_{instance.id}.{ext}"
        return f"profile_images/{self.sub_path}/{new_filename}"


class Account(AbstractBaseUser):
    """Кастомная модель пользователя"""

    email = models.EmailField(verbose_name="Email", max_length=60, unique=True)
    first_name = models.CharField(verbose_name="Имя", max_length=255)
    last_name = models.CharField(verbose_name="Фамилия", max_length=255)
    sur_name = models.CharField(verbose_name="Отчество", max_length=255, null=True)
    balance = models.DecimalField(
        verbose_name="Баланс", max_digits=12, decimal_places=2, default=0
    )
    profile_image = models.ImageField(
        upload_to=UserImagePath("profile_images"), blank=True, null=True
    )
    purchases = models.ManyToManyField(verbose_name="Покупки", to=Purchase, blank=True)
    country = models.CharField(verbose_name="Страна", max_length=255, null=True)
    addresses = models.ManyToManyField(
        to=AccountData, verbose_name="Адреса пользователя", blank=True
    )
    date_joined = models.DateTimeField(
        verbose_name="Дата создания аккаунта", auto_now_add=True
    )
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = AccountManager()

    USERNAME_FIELD = "email"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    def update_balance(self, amount):
        """
        Update the balance of the account by adding the given amount.
        To subtract, pass a negative value for the `amount`.
        """
        self.balance += amount
        self.save()


class Visits(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    last_login = models.DateTimeField(auto_now=timezone.now())
    ip = models.GenericIPAddressField()

    class Meta:
        verbose_name = "Последний визит"
        verbose_name_plural = "Последние визиты"

    def __str__(self):
        return self.account.email


class AccountNotifySettings(models.Model):
    is_telegram_status = models.BooleanField(default=True)
    is_email_status = models.BooleanField(default=True)

    is_telegram_news = models.BooleanField(default=True)
    is_email_news = models.BooleanField(default=True)

    account = models.OneToOneField(Account, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Настройки"
        verbose_name_plural = "Настройки пользовательских уведомлений"

    def __str__(self) -> str:
        return self.account.email


class BuyoutCategory(models.Model):
    name = models.CharField(max_length=255)
    is_visible = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории скуп-листа"

    def __str__(self) -> str:
        return f"({'Включена' if self.is_visible else 'Отключена'}) {self.name}"


class Buyout(models.Model):
    category = models.ForeignKey(BuyoutCategory, on_delete=models.CASCADE)
    name = models.CharField(verbose_name="Товар|Товары", max_length=1024)
    percent = models.DecimalField(
        verbose_name="Процент", max_digits=12, decimal_places=2
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Скуп-лист"

    def __str__(self) -> str:
        return f"{self.category.name} -> {self.name} {self.percent}%"
