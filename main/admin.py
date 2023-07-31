from django.contrib import admin

from . import models


admin.site.register(models.Warehouse)
admin.site.register(models.AccountWarehouse)

