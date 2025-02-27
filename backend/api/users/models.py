import uuid

from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError

from rest_framework.authtoken.models import Token

from api.users.validators import validate_hex_color


class UserManager(BaseUserManager):
    """
    Custom user manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.username = email
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model with email as the unique identifier.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.username


class Profile(models.Model):
    """
    User profile model.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        default=None
    )


class Category(models.Model):
    """
    Category model for organizing notes.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categories',
        null=True,          # Temporarily allow NULL
        blank=True          # So that forms don’t require it
    )
    name = models.CharField(max_length=100)
    color = models.CharField(
        max_length=7,
        validators=[validate_hex_color]
    )

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return f"{self.name}"

    def clean(self):
        """
        Ensure name is not empty or just whitespace
        """
        if not self.name or not self.name.strip():
            raise ValidationError({'name': 'Name cannot be empty or whitespace'})
        self.name = self.name.strip()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def note_count(self):
        """
        Count the number of notes for the category
        """
        return self.notes.count()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token_and_profile(
    sender, instance=None, created=False, **kwargs
):
    """
    Create a token, profile and default categories for new users.
    """
    if created:
        Token.objects.get_or_create(user=instance)
        Profile.objects.get_or_create(user=instance)
