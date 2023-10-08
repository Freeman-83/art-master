from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from colorfield.fields import ColorField

from users.models import CustomUser


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField('Tag', unique=True, max_length=200)
    slug = models.SlugField('Slug', unique=True, max_length=200)
    color = ColorField('Цвет', unique=True, max_length=7)

    class Meta:
        ordering = ['name']
        verbose_name = 'Tag'
        verbose_name_plural = 'Тags'

    def __str__(self):
        return self.name


class Activity(models.Model):
    """Модель вида деятельности."""
    name = models.CharField('Вид деятельности', unique=True, max_length=256)
    tags = models.ManyToManyField(
        Tag,
        through='TagActivity',
        verbose_name='Теги')

    class Meta:
        ordering = ['name']
        verbose_name = 'Activity'
        verbose_name_plural = 'Activities'

    def __str__(self):
        return self.name


class Location(models.Model):
    """Модель локации."""
    address = models.TextField('Адрес')


class Service(models.Model):
    """Модель сервиса."""
    name = models.CharField('Наименование услуги', max_length=256)
    description = models.TextField('Описание', null=False, blank=False)
    master = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Мастер'
    )
    activities = models.ManyToManyField(
        Activity,
        through='ActivityService',
        verbose_name='Вид деятельности'
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagService',
        verbose_name='Теги'
    )
    locations = models.ManyToManyField(
        Location,
        through='LocationService',
        verbose_name='Локации'
    )
    created = models.DateTimeField(
        'Дата размещения информации', auto_now_add=True, db_index=True
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        default_related_name = 'services'

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель отзыва."""
    text = models.TextField('Текст')
    service = models.ForeignKey(
        Service,
        verbose_name='Сервис',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.PositiveSmallIntegerField(
        'Оценка', validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    author = models.ForeignKey(
        CustomUser,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True, db_index=True
    )

    class Meta:
        ordering = ['pub_date']
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        constraints = [
            models.UniqueConstraint(
                fields=['service', 'author'],
                name='unique_review'
            )
        ]


class Comment(models.Model):
    """Модель комментария к отзыву."""
    review = models.ForeignKey(
        Review,
        verbose_name='Отзыв',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField('Текст')
    author = models.ForeignKey(
        CustomUser,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True, db_index=True
    )

    class Meta:
        ordering = ['pub_date']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'


class TagActivity(models.Model):
    """Модель отношений Тег-Вид деятельности."""
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='in_activities'
    )
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='in_tags'
    )

    class Meta:
        ordering = ['tag']
        verbose_name_plural = 'Tags Activities'
        constraints = [
            models.UniqueConstraint(fields=['tag', 'activity'],
                                    name='unique_tag_activity')
        ]

    def __str__(self):
        return f'{self.tag} {self.activity}'


class TagService(models.Model):
    """Модель отношений Тег-Сервис."""
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='in_services'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='in_tags'
    )

    class Meta:
        ordering = ['tag']
        verbose_name_plural = 'Tags Services'
        constraints = [
            models.UniqueConstraint(fields=['tag', 'service'],
                                    name='unique_tag_service')
        ]

    def __str__(self):
        return f'{self.tag} {self.service}'


class ActivityService(models.Model):
    """Модель отношений Вид деятельности-Сервис."""
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
