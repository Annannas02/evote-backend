from django.db import models
from elections.models import Elections
from electionchoice.models import ElectionChoice

class ElectionHistory(models.Model):
    election_id = models.ForeignKey(Elections, on_delete=models.CASCADE)
    choice_id = models.ForeignKey(ElectionChoice, on_delete=models.CASCADE)
    date_inserted = models.DateTimeField()
