from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import DefUser
from .serializer import NameSerializer

class NameView(APIView):
    def get(self, request):
        # Assuming you want to return the first 'Name' instance.
        names = DefUser.objects.all()  # Fetch all names
        serializer = NameSerializer(names, many=True).data  # Serialize the queryset
        return Response(serializer, status=status.HTTP_200_OK)