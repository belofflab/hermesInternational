# Generated by Django 4.2.3 on 2023-09-07 05:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0022_purchasephoto'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='purchase',
            options={'ordering': ['-created'], 'verbose_name': 'Покупка', 'verbose_name_plural': 'Покупки'},
        ),
    ]