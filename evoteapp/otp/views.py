from rest_framework import generics
from otp import models, serializers
from rest_framework import generics

class OtpList(generics.RetrieveUpdateDestroyAPIView):

    queryset = models.OTP.objects.all()
    serializer_class = serializers.OtpSerializer