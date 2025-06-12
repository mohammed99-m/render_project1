from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
import urllib.request
from rest_framework import status

from project.settings import ONESIGNAL_API_KEY, ONESIGNAL_APP_ID
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

from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Notification
from .serializers import NotificationSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
import urllib.request
from onesignal_sdk.client import Client as OneSignalClient

@api_view(["POST"])
def send_notification2(request, user_id):
    serializer = NotificationSerializer(data=request.data)
    if serializer.is_valid():
        notification = serializer.save()

        # Step 1: Fetch user data from external API (e.g., get OneSignal player_id or email)
        external_data = {}
        url = f"https://mohammedmoh.pythonanywhere.com/user/{user_id}/"
        try:
            with urllib.request.urlopen(url) as response:
                external_data = json.load(response)
        except Exception as e:
            external_data = {"error": str(e)}

        # Step 2: Real-time WebSocket notification
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

        # Step 3: Send push notification via OneSignal
        try:
            onesignal_client = OneSignalClient(app_id=ONESIGNAL_APP_ID, rest_api_key=ONESIGNAL_API_KEY)

            # You should extract device identifier like player_id or external_id from external_data
            player_id = external_data.get("player_id")  # Example key
            if player_id:
                onesignal_client.send_notification(
                    contents={"en": notification.content},
                    include_player_ids=[player_id],
                    headings={"en": "New Notification"},
                )
        except Exception as e:
            final_data["onesignal_error"] = str(e)

        return Response(final_data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def send_notification3(request, user_id):
    serializer = NotificationSerializer(data=request.data)
    if serializer.is_valid():
        notification = serializer.save()

        external_data = {}
        player_id = None
        url = f"https://mohammedmoh.pythonanywhere.com/user/{user_id}/"

        try:
            with urllib.request.urlopen(url) as response:
                external_data = json.load(response)
                player_id = external_data.get("player_id")
        except Exception as e:
            external_data = {"error": str(e)}

        final_data = {
            "notification": notification.content,
            "room_name": notification.room_name,
            "player_id": player_id,
        }
        
        print(notification.room_name)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notification_{notification.room_name}',
            {
                'type': 'send_notification',
                'notification': final_data,
            }
        )

        # SEND PUSH
        if player_id:
            try:
                onesignal_client = OneSignalClient(
                    app_id=ONESIGNAL_APP_ID,
                    rest_api_key=ONESIGNAL_API_KEY
                )

                response = onesignal_client.send_notification(
                    notification_body={
                        "include_player_ids": [player_id],
                        "headings": {"en": "New Notification"},
                        "contents": {"en": notification.content}
                    }
                )
                final_data["onesignal_response"] = response.body
               
            except Exception as e:
                final_data["onesignal_error"] = str(e)
        else:
            final_data["onesignal_error"] = "No player_id available"

        return Response(final_data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




##################

@api_view(["POST"])
def send_notification4(request, receiver_id, sender_id):
    serializer = NotificationSerializer(data=request.data)
    if serializer.is_valid():
        notification = serializer.save()

        # Get player_id from external API
        external_data = {}
        player_id = None
        url = f"https://mohammedmoh.pythonanywhere.com/user/{receiver_id}/"

        try:
            with urllib.request.urlopen(url) as response:
                external_data = json.load(response)
                player_id = external_data.get("player_id")
        except Exception as e:
            external_data = {"error": str(e)}

        # Send WebSocket Notification
        final_data = {
            "notification": notification.content,
            "room_name": notification.room_name,
            "player_id": player_id,
        }

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notification_{notification.room_name}',
            {
                'type': 'send_notification',
                'notification': final_data,
            }
        )

        # Send Push Notification via OneSignal
        if player_id:
            try:
                onesignal_client = OneSignalClient(
                    app_id=ONESIGNAL_APP_ID,
                    rest_api_key=ONESIGNAL_API_KEY
                )
                response = onesignal_client.send_notification(
                    notification_body={
                        "include_player_ids": [player_id],
                        "headings": {"en": "New Notification"},
                        "contents": {"en": notification.content}
                    }
                )
                final_data["onesignal_response"] = response.body
            except Exception as e:
                final_data["onesignal_error"] = str(e)
        else:
            final_data["onesignal_error"] = "No player_id available"

#يستدعي تابع حفظ الاشعارات من السيرفر الاساسي ويحفظه
        #sender=f"https://mohammedmoh.pythonanywhere.com/user/{sender_id}/"
        notification_url = "https://mohammedmoh.pythonanywhere.com/notifications/save-notification/"
        headers = {'Content-Type': 'application/json'}
        post_data = json.dumps({
            "receiver": receiver_id,
            "sender": sender_id,
            "content": notification.content,
            "room_name": notification.room_name
        }).encode('utf-8')

        try:
            save_request = urllib.request.Request(
                notification_url,
                method='POST',
                data=post_data,
                headers=headers
            )
            with urllib.request.urlopen(save_request) as save_response:
                if save_response.status == 201:
                    final_data["db_save_status"] = "Notification saved to main server"
                else:
                    final_data["db_save_status"] = f"Failed with status {save_response.status}"
        except Exception as e:
             error_content = e.read().decode()
             final_data["db_save_status"] = f"Error saving notification: {e} - {error_content}"

        return Response(final_data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)