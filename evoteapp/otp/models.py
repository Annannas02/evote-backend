from django.db import models
from users.models import User
from phonenumber_field.modelfields import PhoneNumberField

class OTP(models.Model):
    personid = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    phone = PhoneNumberField(null=False, blank=False, unique=True)