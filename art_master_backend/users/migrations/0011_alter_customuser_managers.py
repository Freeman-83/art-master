# Generated by Django 4.2.6 on 2023-11-07 13:44

from django.db import migrations
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_customuser_phone_number'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='customuser',
            managers=[
                ('objects', users.models.CustomUserManager()),
            ],
        ),
    ]
