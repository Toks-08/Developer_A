from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import TeamSerializer

class MyTeamView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if not user.team:
            return Response(
                {"message": "You are not assigned to any team yet"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TeamSerializer(user.team)
        return Response(serializer.data, status=status.HTTP_200_OK)