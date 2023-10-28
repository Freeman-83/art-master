# Generated by Django 4.2.6 on 2023-10-28 10:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='master',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.master', verbose_name='Мастер'),
        ),
        migrations.AddField(
            model_name='service',
            name='tags',
            field=models.ManyToManyField(through='services.TagService', to='services.tag', verbose_name='Теги'),
        ),
        migrations.AddField(
            model_name='review',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='users.client', verbose_name='Автор'),
        ),
        migrations.AddField(
            model_name='review',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='services.service', verbose_name='Сервис'),
        ),
        migrations.AddField(
            model_name='locationservice',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='in_services', to='services.location'),
        ),
        migrations.AddField(
            model_name='locationservice',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='in_locations', to='services.service'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_services', to='users.client'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='in_favorite_for_clients', to='services.service'),
        ),
        migrations.AddField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AddField(
            model_name='comment',
            name='review',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='services.review', verbose_name='Отзыв'),
        ),
        migrations.AddField(
            model_name='activityservice',
            name='activity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='in_services', to='services.activity'),
        ),
        migrations.AddField(
            model_name='activityservice',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='in_activities', to='services.service'),
        ),
        migrations.AddConstraint(
            model_name='tagservice',
            constraint=models.UniqueConstraint(fields=('tag', 'service'), name='unique_tag_service'),
        ),
        migrations.AddConstraint(
            model_name='review',
            constraint=models.UniqueConstraint(fields=('service', 'author'), name='unique_review'),
        ),
        migrations.AddConstraint(
            model_name='locationservice',
            constraint=models.UniqueConstraint(fields=('location', 'service'), name='unique_location_service'),
        ),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(fields=('client', 'service'), name='unique_favorite'),
        ),
        migrations.AddConstraint(
            model_name='activityservice',
            constraint=models.UniqueConstraint(fields=('activity', 'service'), name='unique_activity_service'),
        ),
    ]