from rest_framework import serializers
from electionchoice import models

class ElectionChoiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ElectionChoice
        fields = '__all__'
    
    def to_representation(self, instance):
        # Exclude 'election_id' only from the output representation
        data = super().to_representation(instance)
        data.pop('election_id', None)
        return data