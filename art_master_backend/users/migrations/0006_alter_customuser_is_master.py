# Generated by Django 4.2.6 on 2023-11-29 09:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_customuser_is_master'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='is_master',
            field=models.BooleanField(default=False, verbose_name='Статус Мастера'),
        ),
    ]