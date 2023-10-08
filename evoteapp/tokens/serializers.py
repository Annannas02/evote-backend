from rest_framework import serializers
from tokens import models

class TokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Token
        fields = '__all__'