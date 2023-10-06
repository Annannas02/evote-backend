from django.db import models
from django.core.validators import MaxLengthValidator, MinLengthValidator

class Elections(models.Model):
    description=models.CharField(max_length=2000)
    city=models.CharField(max_length=150)
