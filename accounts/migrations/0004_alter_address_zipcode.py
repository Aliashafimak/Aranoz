# Generated by Django 4.1.5 on 2023-04-03 04:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='zipcode',
            field=models.IntegerField(null=True),
        ),
    ]
