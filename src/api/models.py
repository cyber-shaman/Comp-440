from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
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

class Feature(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class RentalUnit(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    features = models.ManyToManyField(Feature, through='RentalUnitFeature', related_name='rental_units')
    location = models.CharField(max_length=255, null=True, blank=True)  # Add location field

    def __str__(self):
        return self.title

class RentalUnitFeature(models.Model):
    rental_unit = models.ForeignKey(RentalUnit, on_delete=models.CASCADE)
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('rental_unit', 'feature')

class RentalLimit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'date')

class Review(models.Model):
    RATING_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]

    rental_unit = models.ForeignKey('RentalUnit', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.CharField(max_length=10, choices=RATING_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('rental_unit', 'user')  # Each user can review each rental unit only once

    def __str__(self):
        return f"{self.user} - {self.rental_unit} - {self.rating}"
    


class Review(models.Model):
    RATING_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]

    rental_unit = models.ForeignKey('RentalUnit', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.CharField(max_length=10, choices=RATING_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('rental_unit', 'user')  # Each user can review each rental unit only once

    def __str__(self):
        return f"{self.user} - {self.rental_unit} - {self.rating}"