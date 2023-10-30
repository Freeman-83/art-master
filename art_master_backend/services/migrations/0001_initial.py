# Generated by Django 4.2.6 on 2023-10-30 06:43

import colorfield.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True, verbose_name='Вид деятельности')),
                ('description', models.TextField(verbose_name='Описание')),
                ('slug', models.SlugField(max_length=200, unique=True, verbose_name='Slug')),
            ],
            options={
                'verbose_name': 'Activity',
                'verbose_name_plural': 'Activities',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ActivityService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name_plural': 'Activities Services',
                'ordering': ['activity'],
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Текст')),
                ('pub_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата публикации')),
            ],
            options={
                'verbose_name': 'Comment',
                'verbose_name_plural': 'Comments',
                'ordering': ['pub_date'],
            },
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'ordering': ['service'],
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.TextField(verbose_name='Адрес')),
            ],
        ),
        migrations.CreateModel(
            name='LocationService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name_plural': 'Locations Services',
                'ordering': ['location'],
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Текст')),
                ('score', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)], verbose_name='Оценка')),
                ('pub_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата публикации')),
            ],
            options={
                'verbose_name': 'Review',
                'verbose_name_plural': 'Reviews',
                'ordering': ['pub_date'],
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Наименование услуги')),
                ('description', models.TextField(verbose_name='Описание')),
                ('image', models.ImageField(upload_to='services/image/', verbose_name='Фото')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата размещения информации')),
                ('activities', models.ManyToManyField(through='services.ActivityService', to='services.activity', verbose_name='Вид деятельности')),
                ('locations', models.ManyToManyField(through='services.LocationService', to='services.location', verbose_name='Локации')),
            ],
            options={
                'verbose_name': 'Service',
                'verbose_name_plural': 'Services',
                'ordering': ['name'],
                'default_related_name': 'services',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='Tag')),
                ('slug', models.SlugField(max_length=200, unique=True, verbose_name='Slug')),
                ('color', colorfield.fields.ColorField(default='#FFFFFF', image_field=None, max_length=7, samples=None, unique=True, verbose_name='Цвет')),
            ],
            options={
                'verbose_name': 'Tag',
                'verbose_name_plural': 'Тags',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='TagService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='in_tags', to='services.service')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='in_services', to='services.tag')),
            ],
            options={
                'verbose_name_plural': 'Tags Services',
                'ordering': ['tag'],
            },
        ),
    ]
