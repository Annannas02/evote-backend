from rest_framework import generics
from userhistory import models, serializers
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework import status

class UserHistoryList(generics.RetrieveUpdateDestroyAPIView):

    queryset = models.UserHistory.objects.all()
    serializer_class = serializers.UserHistorySerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_vote_status(request):
    try:
        person_id = request.data.get('person_id')

        # Ensure the provided person ID is valid
        user_vote_entries = models.UserHistory.objects.filter(person_id=person_id)

        # Serialize the UserHistory entries for the response
        serialized_entries = serializers.UserHistorySerializer(user_vote_entries, many=True).data

        return Response(serialized_entries, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_user_vote(request):
    try:
        person_id = request.data.get('person_id')
        election_id = request.data.get('election_id')

        # Ensure the provided user ID is valid
        user_history_entry = get_object_or_404(models.UserHistory, person_id=person_id, election_id=election_id)

        # Delete the UserHistory entry
        user_history_entry.delete()

        return Response({"message": "User vote entry deleted successfully."}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
