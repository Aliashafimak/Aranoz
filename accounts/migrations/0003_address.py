# Generated by Django 4.1.5 on 2023-04-03 04:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_account_otp_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('company', models.CharField(blank=True, max_length=100)),
                ('phone_number', models.CharField(max_length=20)),
                ('email_address', models.EmailField(max_length=100)),
                ('address1', models.CharField(max_length=200)),
                ('address2', models.CharField(blank=True, max_length=200)),
                ('city', models.CharField(max_length=100)),
                ('zipcode', models.IntegerField(max_length=20)),
                ('shipping_address', models.BooleanField(default=True)),
                ('order_note', models.CharField(default='', max_length=500)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]