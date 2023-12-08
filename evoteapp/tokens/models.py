from django.db import models
from users.models import User

class Token(models.Model):
    token_value = models.CharField(max_length=200, null=False)
    voted = models.BooleanField(null=False)
    date_voted = models.DateTimeField(null=True)
    personid= models.ForeignKey(User, on_delete=models.CASCADE)
