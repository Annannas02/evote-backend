from django.db import models
from users.models import User

class Token(models.Model):
    person_id = models.ForeignKey(User, on_delete=models.CASCADE)
    got_token = models.BooleanField()
    date_generate_token=models.DateField()


