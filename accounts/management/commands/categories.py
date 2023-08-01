from django.core.management.base import BaseCommand
import json
from accounts.models import BuyoutCategory, Buyout
data = {
    "APPLE Iphone":
    {
         "Apple Iphone 14/14 Plus, Apple Iphone 14 Pro/Pro Max (unlocked) ": 60,
        "Apple Iphone 13, Apple Iphone 13 mini, Apple Iphone 13 Pro/Pro Max (unlocked)" : 50,
        "Apple Iphone 12, 12 Pro (unlocked)" : 40,
        "Apple Iphone SE (unlocked)" : 40,
        "Refurbished заводской" : 35,
    },
     "Apple MacBook ":
    {
         "Apple MacBook 2021 M1, 2022 M2 ": 50,
         "Apple MacBook 2019:2020 ": 40,
         "Apple MacBook 2018 ": 45,
         "Apple IMac M1 ": 40,
    },
    "Apple IPad":
    {
        "Apple IPad Pro New 11, 12.9 (до 512Gb)": 50,
        "Apple IPad Pro New 11, 12.9 (от 1Tb)": 40,
        "Apple IPad Pro New 11, 12.9 + Cellular (до 512Gb)": 45,
        "Apple IPad Air": 45,
        "Apple IPad New 10.2": 40,
        "Apple IPad Mini 2021": 45
    },
    "Apple Watch":
    {
        "Apple Watch Series 8/Ultra": 50
    },
    "Apple AirPods":
    {
        "Apple Airpods Pro 2": 45,
        "Apple AirPods (3rd Generation)": 40,
        "Apple Airpods Max": 45
    },
    "Apple Pencil":
    {
        "Apple Pencil 2": 40
    },
    "Ноутбуки":
    {
        "Только с intel 13 gen": 0,
        "ASUS ROG, MSI Gaming, Microsoft Surface": 35,
        "Asus, Acer Predator, Lenovo, Dell, HP": 35
    },
    "Компьютерные комплектующие":
    {
        "Видеокарты Asus, Gigabyte, MSI, EVGA, Zotac 40**": 40,
        "Видеокарты Asus, Gigabyte, MSI, EVGA, Zotac 30**": 30,
        "Процессоры i7, i9 12 серии": 40,
        "SSD от 1TB Samsung, Kingston, HyperX, Western Digital, ADATA, Intel, Corsair (от 2 в паке)": 35,
        "Oculus Quest 2 VR Headset": 40,
        "Sony PS5 Playstation 5": 35,
        "Xbox Series X": 35,
        "Steam Deck": 50
    },
    "Мобильные телефоны":
    {
         "Samsung S23, S23+, S23 Ultra ": 45,
        "Samsung Fold4, Flip4": 40,
        "Google Pixel 7/7 Pro": 45
    },
    "Фото:видео камеры":
    {
         "Gopro 11 ": 50,
        "Gopro Max": 40,
        "Sony Action Cam": 35,
        "Фотоаппараты Canon, Nikon": 35,
        "Объективы/вспышки Canon, Nikon": 35
    },
    "Коптеры":
    {
        "DJI Mavic 3": 40,
        "DJI Mavic 2": 35,
        "DJI Inspire 2": 35,
        "DJI Mavic Air": 35,
        "DJi Mavic Pro": 35,
        "Прочие модели от DJI": 35
    },
    "DJ оборудование":
    {
        "Pioneer DJ XDJ-1000MK2": 40,
        "Pioneer CDJ-3000": 40,
        "Pioneer DJM900NXS2": 40,
        "Pioneer PRO DJ DJMS7": 40
    },
    "Эхолоты":
    {
         "Garmin ": 35,
         "Humminbird ": 35,
         "Lowrance ": 35,
         "Raymarine ": 35
    },
    "Тепловизионное оборудование":
    {
         "Seek Reveal ": 35,
         "FLIR ": 35 
    },
    "Прочее":
    {
         "Наушники, акустика Beats , Marshal и тд ": 20,
         "Техника Dyson ": 25,
         "Tesla Wall Connector/ Tesla CHAdeMO Adapter ": 35
    },
    "Драгоценные металлы":
    {
        "Золото в монетах и слитках": 35,
        "Золото в украшениях и тд.": 40,
        "Платина в монетах и слитках": 35,
         "Серебро в монетах и слитках ": 35
    }
}

class Command(BaseCommand):
    def handle(self, *args, **options):
        for category in data:
            category_model = BuyoutCategory.objects.create(
                name=category,
                is_visible=True
            )
            for item in data[category]:
                Buyout.objects.create(
                    category=category_model,
                    name=item,
                    percent=data[category][item]
                )

