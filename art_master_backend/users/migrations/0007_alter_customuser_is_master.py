# Generated by Django 4.2.6 on 2023-12-01 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_customuser_is_master'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='is_master',
            field=models.BooleanField(verbose_name='Статус Мастера'),
        ),
    ]
