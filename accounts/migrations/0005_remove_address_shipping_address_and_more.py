# Generated by Django 4.1.5 on 2023-04-03 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_address_zipcode'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='shipping_address',
        ),
        migrations.AddField(
            model_name='address',
            name='billing_address',
            field=models.BooleanField(default=False),
        ),
    ]
