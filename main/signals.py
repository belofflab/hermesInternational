from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import AccountWarehouse, Warehouse, WarehouseShop

shops = [
    {"name": "amazon", "image": "img/shops/amazon.svg"},
    {"name": "ebay", "image": "img/shops/ebay.svg"},
    {"name": "nike", "image": "img/shops/nike.svg"},
    {"name": "adidas", "image": "img/shops/adidas.svg"},
    {"name": "zara", "image": "img/shops/zara.svg"},
    {"name": "apple", "image": "img/shops/apple.svg"},
    {"name": "asos", "image": "img/shops/asos.svg"},
    {"name": "bestbuy", "image": "img/shops/best_buy.svg"},
    # {"name": "New Egg", "image": "img/shops/new_egg.svg"},
    # {"name": "Nordstorm", "image": "img/shops/nordstorm.svg"},
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
