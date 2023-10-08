from rest_framework import generics
from electionchoice import models, serializers
from rest_framework import generics

class ElectionChoiceList(generics.RetrieveUpdateDestroyAPIView):

    queryset = models.ElectionChoice.objects.all()
    serializer_class = serializers.ElectionChoiceSerializer