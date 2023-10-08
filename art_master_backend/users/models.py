from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""
    USER = 'user'
    MASTER = 'master'
    ADMIN = 'admin'
    ROLE_CHOICES = [(USER, 'user'),
                    (MASTER, 'master'),
                    (ADMIN, 'admin'),]
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    email = models.EmailField(
        _('email address'),
        max_length=254,
        unique=True,
        null=False,
        blank=False
    )
    bio = models.TextField('О себе', null=True, blank=True)
    role = models.CharField(
        'Статус',
        max_length=9,
        choices=ROLE_CHOICES,
        default=USER
    )
    foto = models.ImageField(
        'Фото профиля',
        upload_to='users/image/',
        null=True,
        blank=True
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

    def is_admin(self):
        return self.is_staff or self.role == "admin"

    def is_master(self):
        return self.role == "master"

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    "Модель подписок."
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    master = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )

    class Meta:
        ordering = ['master']
        constraints = [
            models.UniqueConstraint(fields=['user', 'master'],
                                    name='unique_subscribe')
        ]

    def __str__(self):
        return f'{self.user} {self.master}'
