
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone


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


class Account(AbstractBaseUser):
    """Кастомная модель пользователя"""

    email = models.EmailField(verbose_name="Email", max_length=60, unique=True)
    first_name = models.CharField(verbose_name="Имя", max_length=255)
    last_name = models.CharField(verbose_name="Фамилия", max_length=255)
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


class Visits(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    last_login = models.DateTimeField(auto_now=timezone.now())
    ip = models.GenericIPAddressField()

    class Meta:
        verbose_name = "Последний визит"
        verbose_name_plural = "Последние визиты"

    def __str__(self):
        return self.account.email
