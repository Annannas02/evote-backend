from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.contrib.auth.models import AbstractBaseUser

class User(AbstractBaseUser):
    idnp = models.CharField(unique=True,max_length=13, validators=[MinLengthValidator(limit_value=13)])
    phone = PhoneNumberField(null=False, blank=False, unique=True)
    secret = models.CharField(max_length=17, null=True)

    #last_login = models.DateField()
    #is_staff = models.BooleanField(default=False)

    USERNAME_FIELD='idnp'

