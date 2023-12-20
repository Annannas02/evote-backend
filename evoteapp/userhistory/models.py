from django.db import models
from users.models import User
from elections.models import Elections


class UserHistory(models.Model):
    election_id= models.ForeignKey(Elections, on_delete=models.CASCADE)
    date_voted = models.DateTimeField(null=False)
    person_id= models.ForeignKey(User, on_delete=models.CASCADE)
