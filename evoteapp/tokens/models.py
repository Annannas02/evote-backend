from django.db import models
from users.models import User

class Token(models.Model):
    person = models.ForeignKey(User, on_delete=models.CASCADE)
    token_value = models.CharField(max_length=200, null=False)
    voted = models.BooleanField()
    date_voted = models.DateTimeField()

