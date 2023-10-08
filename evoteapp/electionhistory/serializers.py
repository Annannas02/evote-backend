from rest_framework import serializers
from electionhistory import models

class ElectionHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ElectionHistory
        fields = '__all__'