# Generated by Django 4.2.6 on 2023-11-02 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0005_remove_location_address_location_building_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='phone_number',
            field=models.CharField(blank=True, max_length=11, null=True, verbose_name='Номер телефона'),
        ),
        migrations.AddField(
            model_name='service',
            name='social_network_contacts',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Ссылка на аккаунт в социальных сетях'),
        ),
    ]