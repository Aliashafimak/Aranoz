# Generated by Django 4.1.5 on 2023-03-21 04:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='otp_code',
            field=models.CharField(blank=True, max_length=6),
        ),
    ]