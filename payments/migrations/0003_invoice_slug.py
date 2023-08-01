# Generated by Django 4.2.3 on 2023-08-01 05:48

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_alter_invoice_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='slug',
            field=models.CharField(default=uuid.uuid4, max_length=1024, verbose_name='SLUG'),
        ),
    ]
