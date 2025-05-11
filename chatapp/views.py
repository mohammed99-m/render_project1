import json
import urllib.request
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Message
from .serializers import MessageSerializer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

@api_view(["POST"])
def SendMessageView(request,user_id):
    print("K" * 50)
    serializer = MessageSerializer(data=request.data)
    if serializer.is_valid():
        message = serializer.save()

        # Step 1: Call external server using urllib
        external_data = {}
        url = "https://mohammedmoh.pythonanywhere.com/user/{user_id}/"
        try:
            print("H" * 50)
            with urllib.request.urlopen(url) as response:
                external_data = json.load(response)
        except Exception as e:
            external_data = {"error": str(e)}

        # Step 2: Create final response data
        final_data = {
            "message": message.content,
            "room_name": message.room_name,
            "external_result": external_data
        }

        # Step 3: Broadcast to WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{message.room_name}",
            {
                "type": "chat_message",
                "message": final_data,
            }
        )

        # Step 4: Return the same data to the API client
        return Response(final_data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
