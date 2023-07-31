# Generated by Django 4.2.3 on 2023-07-31 13:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0002_alter_warehouse_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountWarehouse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.warehouse')),
            ],
            options={
                'verbose_name': 'Склад',
                'verbose_name_plural': 'Склады пользователей',
            },
        ),
    ]
