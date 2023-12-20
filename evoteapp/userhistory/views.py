from rest_framework import generics
from userhistory import models, serializers
from rest_framework import generics

class UserHistoryList(generics.RetrieveUpdateDestroyAPIView):

    queryset = models.UserHistory.objects.all()
    serializer_class = serializers.UserHistorySerializer