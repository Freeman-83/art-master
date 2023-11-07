from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import UserManager

from django.db.models import Q


class CustomUserManager(UserManager):

    def get_by_natural_key(self, username):
        return self.get(
            Q(**{self.model.USERNAME_FIELD: username}) or Q(**{self.model.PHONE_FIELD: username})
        )


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""
    username = models.CharField('Логин', max_length=150, unique=True)
    email = models.EmailField(
        _('email'),
        max_length=254,
        unique=True,
        null=False,
        blank=False
    )
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    photo = models.ImageField(
        'Фото профиля',
        upload_to='users/image/',
        null=True,
        blank=True
    )
    phone_number = models.CharField('Номер телефона', max_length=11)
    is_master = models.BooleanField('Статус Мастера', default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    PHONE_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username', 'password']

    class Meta:
        ordering = ['username']
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_user'
            ),
        ]


class Subscribe(models.Model):
    """Модель подписок."""
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    master = models.ForeignKey(
        settings.AUTH_USER_MODEL,
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
