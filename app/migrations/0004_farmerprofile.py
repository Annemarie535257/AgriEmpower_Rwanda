# Generated by Django 5.1.2 on 2024-11-11 11:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_alter_cooperative_user_alter_farmer_user_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FarmerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=100)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('farm_name', models.CharField(blank=True, max_length=255, null=True)),
                ('farm_location', models.CharField(blank=True, max_length=255, null=True)),
                ('farm_size', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('crop_type', models.CharField(blank=True, max_length=100, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
