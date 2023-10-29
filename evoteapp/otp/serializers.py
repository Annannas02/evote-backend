from rest_framework import serializers
from otp import models

class OtpSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.OTP
        fields = '__all__'