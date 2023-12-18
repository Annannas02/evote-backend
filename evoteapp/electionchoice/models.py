from django.db import models
from elections.models import Elections

class ElectionChoice(models.Model):
    election_id = models.ForeignKey(Elections, on_delete=models.CASCADE)
    description = models.CharField(max_length=2000)
    img = models.CharField(max_length=50)
    
    
