# Generated by Django 4.2.6 on 2023-10-30 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='site_address',
            field=models.URLField(blank=True, null=True, verbose_name='Сайт'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='social_network_contacts',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Ссылка на аккаунт в социальных сетях'),
        ),
    ]