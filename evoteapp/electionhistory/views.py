from rest_framework import generics
from elections import models as electionmodels
from electionchoice import models as electionchoicemodel
from tokens import models as tokenmodels
from users import models as usermodels
from userhistory import models as userhistorymodel
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


#TODO: REWORK THESE 2 ENDPOINTS

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

        # Get the corresponding Elections and ElectionChoice instances
        election = get_object_or_404(electionmodels.Elections, id=election_id)
        choice = get_object_or_404(electionchoicemodel.ElectionChoice, id=choice_id)

        # Check if the user has voted for the same election before
        user_history_entry = userhistorymodel.UserHistory.objects.filter(person_id=user, election_id=election).first()
        if user_history_entry:
            return Response({"error": "User has already voted in this election."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Create UserHistory entry
        userhistorymodel.UserHistory.objects.create(person_id=user, election_id=election, date_voted=timezone.now().date())

        # Create ElectionHistory object and save it to the database
        election_history = models.ElectionHistory.objects.create(
            election_id=election,
            choice_id=choice,
            date_inserted=timezone.now()
        )

        # Serialize the created ElectionHistory object for the response
        serialized_election_history = serializers.ElectionHistorySerializer(election_history).data

        return Response(serialized_election_history, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def delete_user_vote(request):
    try:
        user_id = request.data.get('user_id')
        election_id = request.data.get('election_id')

        # Ensure the provided user ID is valid
        user_history_entry = get_object_or_404(userhistorymodel.UserHistory, personid=user_id, electionid=election_id)

        # Delete the UserHistory entry
        user_history_entry.delete()

        return Response({"message": "User vote entry deleted successfully."}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

