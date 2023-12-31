# Generated by Django 4.2.3 on 2023-07-29 16:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_purchase_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountNotifySettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_telegram_status', models.BooleanField(default=True)),
                ('is_email_status', models.BooleanField(default=True)),
                ('is_telegram_news', models.BooleanField(default=True)),
                ('is_email_news', models.BooleanField(default=True)),
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
