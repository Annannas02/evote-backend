from django.db import models
from django.core.validators import MinLengthValidator

class Elections(models.Model):
    description=models.CharField(max_length=2000)
    electionimage = models.ImageField(upload_to='election_images/', null=True, blank=True)
    year = models.CharField(max_length=4)
