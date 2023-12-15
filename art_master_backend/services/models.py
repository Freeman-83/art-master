from django.conf import settings
from django.contrib.gis.db import models as gismodels
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from colorfield.fields import ColorField

from phonenumber_field.modelfields import PhoneNumberField


class Activity(models.Model):
    """Модель Активности."""
    name = models.CharField('Вид деятельности', unique=True, max_length=256)
    description = models.TextField('Описание', null=False, blank=False)
    slug = models.SlugField('Slug', unique=True, max_length=200)

    class Meta:
        ordering = ['name']
        verbose_name = 'Activity'
        verbose_name_plural = 'Activities'

    def __str__(self):
        return self.name


class Location(gismodels.Model):
    """Модель Локации."""
    address = models.CharField(
        verbose_name='Адрес',
        max_length=256
    )
    point = gismodels.PointField(spatial_index=True)

    class Meta:
        ordering = ['address']
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'

    def __str__(self):
        return self.address


class Service(models.Model):
    """Модель Сервиса."""
    name = models.CharField('Наименование услуги', max_length=256)
    description = models.TextField('Описание', null=False, blank=False)
    master = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Мастер',
        related_name='services'
    )
    activities = models.ManyToManyField(
        Activity,
        through='ActivityService',
        verbose_name='Вид деятельности'
    )
    locations = models.ManyToManyField(
        Location,
        through='LocationService',
        verbose_name='Локации'
    )
    image = models.ImageField('Фото', upload_to='services/image/')
    about_master = models.TextField('О себе', null=True, blank=True)
    site_address = models.URLField(
        'Адрес сайта',
        null=True,
        blank=True
    )
    phone_number = PhoneNumberField('Контактный номер телефона')
    social_network_contacts = models.CharField(
        'Ссылка на аккаунт в социальных сетях',
        max_length=100,
        null=True,
        blank=True
    )
    created = models.DateTimeField(
        'Дата размещения информации', auto_now_add=True, db_index=True
    )

    class Meta:
        ordering = ['-created']
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        default_related_name = 'services'

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель Отзыва."""
    service = models.ForeignKey(
        Service,
        verbose_name='Сервис',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField('Текст')
    score = models.PositiveSmallIntegerField(
        'Оценка', validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True, db_index=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        constraints = [
            models.UniqueConstraint(
                fields=['service', 'author'],
                name='unique_review'
            )
        ]


class Comment(models.Model):
    """Модель Комментария к Отзыву."""
    review = models.ForeignKey(
        Review,
        verbose_name='Отзыв',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField('Текст')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True, db_index=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'


class ActivityService(models.Model):
    """Модель отношений Активность-Сервис."""
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='in_services'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='in_activities'
    )

    class Meta:
        ordering = ['activity']
        verbose_name_plural = 'Activities Services'
        constraints = [
            models.UniqueConstraint(fields=['activity', 'service'],
                                    name='unique_activity_service')
        ]

    def __str__(self):
        return f'{self.activity} {self.service}'


class LocationService(models.Model):
    """Модель отношений Локация-Сервис."""
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='in_services'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='in_locations'
    )

    class Meta:
        ordering = ['location']
        verbose_name_plural = 'Locations Services'
        constraints = [
            models.UniqueConstraint(fields=['location', 'service'],
                                    name='unique_location_service')
        ]

    def __str__(self):
        return f'{self.location} {self.service}'


class Favorite(models.Model):
    """Модель избранных Сервисов."""
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_services'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='in_favorite_for_clients'
    )

    class Meta:
        ordering = ['service']
        constraints = [
            models.UniqueConstraint(fields=['client', 'service'],
                                    name='unique_favorite')
        ]

    def __str__(self):
        return f'{self.client} {self.service}'
