# Generated by Django 4.2.3 on 2023-07-26 06:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='invoice',
            options={'ordering': ['-created_at'], 'verbose_name': 'Чек', 'verbose_name_plural': 'Чеки'},
        ),
    ]