from django.db import models
from users.models import User

class Token(models.Model):
    token_value = models.CharField(max_length=6, null=False, unique=True)
    creation_date= models.DateTimeField(null=False)
    personid= models.ForeignKey(User, on_delete=models.CASCADE)
