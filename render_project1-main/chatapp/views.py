import json
import urllib.request
import requests
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
    print(user_id)
    key = str(user_id)
    print(key)
    serializer = MessageSerializer(data=request.data)
    if serializer.is_valid():
        message = serializer.save()

        # Step 1: Call external server using urllib
        external_data = {}
        url = f"https://mohammedmoh.pythonanywhere.com/user/{user_id}/"
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

#يجب اضافة المستقبل ضمن جسم تابع ارسال الرسالة 
        receiver_id = request.data.get("receiver_id")


        if receiver_id:
            notification_message = f"You have a new message"
            notification_url = f"http://127.0.0.1:8000/notification/send-notifications/{receiver_id}/"


            notification_data={
                "content": notification_message,
                "user_id": receiver_id,
                "room_name": f"user_{receiver_id}"
            }

            try:
                response = requests.post(notification_url, json=notification_data)
                print("Notification sent:", response.status_code, response.text)
            except Exception as e:
                print("Failed to send notification:", str(e))
                 

        # Step 4: Return the same data to the API client
        return Response(final_data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
