from rest_framework import generics
from django.shortcuts import get_object_or_404
from elections import models, serializers
from electionchoice.models import ElectionChoice
from electionchoice.serializers import ElectionChoiceSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import generics, status

class ElectionsList(generics.ListCreateAPIView):
    
    queryset = models.Elections.objects.all()
    serializer_class = serializers.ElectionSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_elections(request):
    try:
        # Get all elections
        elections = models.Elections.objects.all()

        # Serialize the elections data
        serialized_elections = serializers.ElectionSerializer(elections, many=True).data

        # Iterate through each election to retrieve and serialize its choices
        for election_data in serialized_elections:
            election_id = election_data['id']
            choices = ElectionChoice.objects.filter(election_id=election_id)
            serialized_choices = ElectionChoiceSerializer(choices, many=True).data
            election_data['choices'] = serialized_choices

        return Response(serialized_elections, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_election_by_id(request, election_id):
    try:
        # Get the election instance or return a 404 response if not found
        election = get_object_or_404(models.Elections, id=election_id)

        # Serialize the election data
        serialized_election = serializers.ElectionSerializer(election).data

        # Retrieve and serialize the choices for the election
        choices = ElectionChoice.objects.filter(election_id=election_id)
        serialized_choices = ElectionChoiceSerializer(choices, many=True).data
        serialized_election['choices'] = serialized_choices

        return Response(serialized_election, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)