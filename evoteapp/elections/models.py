from django.db import models
from django.core.validators import MinLengthValidator

class Elections(models.Model):
    description=models.CharField(max_length=2000)
    img = models.CharField(max_length=50)
    year = models.CharField(max_length=4)
