from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractBaseUser 
from django.core.validators import MaxLengthValidator, MinLengthValidator

class User(AbstractBaseUser):
    reg_date = models.DateField(auto_now=True)
    idnp = models.PositiveIntegerField(unique=True, validators=[MinLengthValidator(limit_value=13), MaxLengthValidator(limit_value=13)])
    phone = PhoneNumberField(null=False, blank=False, unique=True)
    last_login = models.DateField()
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone'
