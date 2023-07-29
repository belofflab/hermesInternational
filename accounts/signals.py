from django.dispatch import receiver
from .models import Account, AccountNotifySettings
from django.db.models.signals import post_save


@receiver(post_save, sender=Account)
def post_save_account(created, **kwargs):
      if created:
            AccountNotifySettings.objects.create()
