from rest_framework import serializers
from userhistory import models

class UserHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.UserHistory
        fields = '__all__'