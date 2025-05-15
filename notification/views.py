from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
import urllib.request
from rest_framework import status
from .models import Notification
from .serializers import Notification, NotificationSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


# @api_view(['POST'])
# def send_notification(request, user_id):
#     message_content = request.data.get("message")
#     room_name = request.data.get("room_name")  # تأكد من الحصول على room_name

#     if message_content and room_name:
#         # استدعاء notify_user لإرسال الإشعار
#         async_to_sync(notify_user)(room_name, message_content)

#         return Response({"message": "Notification sent successfully"}, status=status.HTTP_201_CREATED)
#     return Response({"error": "Invalid input"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def send_notification(request, user_id):
    serializer = NotificationSerializer(data=request.data)
    if serializer.is_valid():
        notification = serializer.save()

        
        external_data = {}
        url = f"https://mohammedmoh.pythonanywhere.com/user/{user_id}/"
        try:
            with urllib.request.urlopen(url) as response:
                external_data = json.load(response)
        except Exception as e:
            external_data = {"error": str(e)}

        final_data = {
            "notification": notification.content,
            "room_name": notification.room_name,
            "external_result": external_data
        }
        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            f'notification_{notification.room_name}',
            {
                'type': 'send_notification',
                'notification': final_data,
            }
        )

        return Response(final_data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)