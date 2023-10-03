import re

from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone

from accounts.models import Purchase

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
    if instance.is_opened and not instance.opened_date:
        instance.opened_date = timezone.now()
        instance.save()
    if created:
        for shop in shops:
            WarehouseShop.objects.create(warehouse=instance, **shop)


@receiver(post_delete, sender=Purchase)
def update_warehouse_shop_quantity(sender, instance, **kwargs):
    def update_warehouse_quantity(url: str, shops):
        match = re.search(r"(www\.)?(\w+\.\w+)", url)
        matched_shop = match.group(2)

        for shop in shops:
            if matched_shop.startswith(shop.name):
                shop.quantity = shop.quantity - 1
                shop.save()

    if instance.delivery_warehouse:
        try:
            wss = WarehouseShop.objects.filter(
                content_type=ContentType.objects.get_for_model(
                    instance.delivery_warehouse
                ),
                object_id=instance.delivery_warehouse.id,
            ).all()
            update_warehouse_quantity(url=instance.link, shops=wss)
        except WarehouseShop.DoesNotExist:
            print("Not Found model WarehouseShop")
