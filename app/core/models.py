from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):  # default password known for testing
        # create, save and return a new user
        if not email:
            raise ValueError('User must have an email')
        user = self.model(email=self.normalize_email(email),
                          **extra_fields)  # name..etc. will be provided in the **extra_fields
        user.set_password(password)  # set_password hashes the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):  # name here is important this will trigger django manage CLI
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    # User in the system
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()  # assign the model to that user manager

    USERNAME_FIELD = 'email'  # this will be used for authentication session not the username
