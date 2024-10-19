from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    phoneNumber = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    # Specify related_name attributes to avoid conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  # Custom related name to avoid conflict
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',  # Custom related name to avoid conflict
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )
