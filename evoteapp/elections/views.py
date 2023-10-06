from rest_framework import generics
from elections import models, serializers


class ElectionsList(generics.ListCreateAPIView):
    
    queryset = models.Elections.objects.all()
    serializer_class = serializers.ElectionSerializer