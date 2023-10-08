from rest_framework import serializers
from elections import models

class ElectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Elections
        fields = '__all__'