from rest_framework import generics
from elections import models as electionmodels
from electionchoice import models as electionchoicemodel
from tokens import models as tokenmodels
from users import models as usermodels
from electionhistory import models, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.utils import timezone

class ElectionHistoryList(generics.RetrieveUpdateDestroyAPIView):

    queryset = models.ElectionHistory.objects.all()
    serializer_class = serializers.ElectionHistorySerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def vote(request):
    try:
        election_id = request.data.get('election_id')
        choice_id = request.data.get('choice_id')

        # Validate that both election_id and choice_id are provided
        if not election_id or not choice_id:
            return Response({"error": "Both election_id and choice_id are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        # Check if the user has a Token entry
        token_entry = get_object_or_404(tokenmodels.Token, personid=user)

        # Check if the user has already voted
        if token_entry.voted:
            return Response({"error": "User has already voted."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Get the corresponding Elections and ElectionChoice instances
        election = get_object_or_404(electionmodels.Elections, id=election_id)
        choice = get_object_or_404(electionchoicemodel.ElectionChoice, id=choice_id)

        # Create ElectionHistory object and save it to the database
        election_history = models.ElectionHistory.objects.create(
            election_id=election,
            choice_id=choice,
            date_inserted=timezone.now()
        )
        # Update the Token entry after the vote is submitted
        token_entry.voted = True
        token_entry.date_voted = timezone.now()
        token_entry.save()

        # Serialize the created ElectionHistory object for the response
        serialized_election_history = serializers.ElectionHistorySerializer(election_history).data

        return Response(serialized_election_history, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def set_vote_status(request):
    try:
        user_id = request.data.get('id')
        voted_status = request.data.get('voted')

        # Ensure the provided user ID is valid
        user = get_object_or_404(usermodels.User, id=user_id)

        # Update the vote status in the Token table
        token = tokenmodels.Token.objects.get(personid=user)
        if not token:
            return Response({"error": "User doesn't have a token yet."},
                            status=status.HTTP_404_NOT_FOUND)
        token.voted = voted_status
        token.save()

        return Response({"message": "Vote status updated successfully."}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

