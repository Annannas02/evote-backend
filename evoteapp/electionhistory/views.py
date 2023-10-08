from rest_framework import generics
from electionhistory import models, serializers
from rest_framework import generics

class ElectionHistoryList(generics.RetrieveUpdateDestroyAPIView):

    queryset = models.ElectionHistory.objects.all()
    serializer_class = serializers.ElectionHistorySerializer