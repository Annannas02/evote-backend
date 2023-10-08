from rest_framework import serializers
from electionchoice import models

class ElectionChoiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ElectionChoice
        fields = '__all__'