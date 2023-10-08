from rest_framework import generics
from tokens import models, serializers
from rest_framework import generics

class TokenList(generics.RetrieveUpdateDestroyAPIView):

    queryset = models.Token.objects.all()
    serializer_class = serializers.TokenSerializer