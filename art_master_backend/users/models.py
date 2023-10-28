from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """Кастомная базовая модель пользователя."""

    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    email = models.EmailField(
        _('email'),
        max_length=254,
        unique=True,
        null=False,
        blank=False
    )

    REQUIRED_FIELDS = ['email', 'password']

    class Meta:
        ordering = ['username']
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_user'
            ),
        ]


class Client(CustomUser):
    "Кастомная модель Клиента."

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    def __str__(self):
        return self.username


class Master(CustomUser):
    "Кастомная модель Мастера."
    bio = models.TextField('О себе')
    photo = models.ImageField(
        'Фото профиля',
        upload_to='users/image/',
        null=True,
        blank=True
    )
    phone_number = models.CharField('Номер телефона', max_length=11)

    REQUIRED_FIELDS = ['email', 'password']

    class Meta:
        verbose_name = 'Master'
        verbose_name_plural = 'Masters'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    """Модель подписок."""
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    master = models.ForeignKey(
        Master,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )

    class Meta:
        ordering = ['master']
        constraints = [
            models.UniqueConstraint(fields=['client', 'master'],
                                    name='unique_subscribe')
        ]

    def __str__(self):
        return f'{self.client} {self.master}'
