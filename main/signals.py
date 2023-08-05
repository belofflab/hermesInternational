from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import AccountWarehouse, Warehouse, WarehouseShop

shops = [
    {"name": "Apple", "image": "img/shops/apple.png"},
    {"name": "AT&T", "image": "img/shops/att.png"},
    {"name": "Best Buy", "image": "img/shops/best_buy.png"},
    {"name": "Body Building", "image": "img/shops/body_building.png"},
    {"name": "New Egg", "image": "img/shops/new_egg.png"},
    {"name": "Nordstorm", "image": "img/shops/nordstorm.png"},
]


@receiver(post_save, sender=Warehouse)
def post_save_warehouse(created, instance, **kwargs):
    if created:
        for shop in shops:
            WarehouseShop.objects.create(warehouse=instance, **shop)


@receiver(post_save, sender=AccountWarehouse)
def post_save_account_warehouse(created, instance, **kwargs):
    if created:
        for shop in shops:
            WarehouseShop.objects.create(warehouse=instance, **shop)
