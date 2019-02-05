from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.conf import settings


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
            Creates and saves a new user.
        """
        # Check if the email was given
        if not email:
            raise ValueError('Users must have an email address')

        # Create the user and save it
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        # Return the user
        return user

    def create_superuser(self, email, password):
        """
            Creates and saves a new superuser.
        """
        # Create a normal user and set to a superuser
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        # Return the user
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
        Custom user model that supports using email
        instead of username.
    """
    # Model fields
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Assign the user manager to the objects attribute
    objects = UserManager()

    # Set the email as the username
    USERNAME_FIELD = 'email'


class Tag(models.Model):
    """
        Tag to be used for recipes.
    """
    name = models.CharField(max_length=50)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name
