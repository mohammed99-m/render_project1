from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Message
from .serializers import MessageSerializer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class SendMessageView(APIView):
    def post(self, request):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save()

            # Broadcast to WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"chat_{message.room_name}",
                {
                    "type": "chat_message",
                    "message": message.content,
                }
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
