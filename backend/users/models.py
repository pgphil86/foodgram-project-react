from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    '''
    Model of user.
    '''
    REGEX = r'^[\w.@+-]+\Z'

    email = models.EmailField(
        max_length=settings.EMAIL_LENGTH,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Email'
    )
    first_name = models.CharField(
        max_length=settings.FIELD_LENGTH,
        blank=True,
        verbose_name='Name'
    )
    last_name = models.CharField(
        max_length=settings.FIELD_LENGTH,
        blank=True,
        verbose_name='Surname'
    )
    password = models.CharField(
        max_length=settings.FIELD_LENGTH,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Password'
    )
    username = models.CharField(
        max_length=settings.FIELD_LENGTH,
        unique=True,
        blank=False,
        null=False,
        validators=[RegexValidator(REGEX)],
        verbose_name='Login'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_user'
            )
        ]

    def __str__(self):
        return self.username


class Follow(models.Model):
    '''
    Model of subscription and editing it.
    '''

    reader = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Reader'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Author'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('reader', 'author'),
                name='unique_follow'
            ),
            models.CheckConstraint(
                name='It is impossible to subscribe to yourself.',
                check=models.Q(author=models.F('reader'))
            ),
        ]
        ordering = ('author',)
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'

    def __str__(self):
        return f'{self.user.username} follows {self.author.username}'
