import json
import urllib.request
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Message
from .serializers import MessageSerializer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# @api_view(["POST"])
# def SendMessageView(request,user_id):
#     print("K" * 50)
#     print(user_id)
#     key = str(user_id)
#     print(key)
#     serializer = MessageSerializer(data=request.data)
#     if serializer.is_valid():
#         message = serializer.save()

#         # Step 1: Call external server using urllib
#         external_data = {}
#         url = f"https://mohammedmoh.pythonanywhere.com/user/{user_id}/"
#         try:
#             print("H" * 50)
#             with urllib.request.urlopen(url) as response:
#                 external_data = json.load(response)
#         except Exception as e:
#             external_data = {"error": str(e)}

#         # Step 2: Create final response data
#         final_data = {
#             "message": message.content,
#             "room_name": message.room_name,
#             "external_result": external_data
#         }

#         # Step 3: Broadcast to WebSocket
#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.group_send)(
#             f"chat_{message.room_name}",
#             {
#                 "type": "chat_message",
#                 "message": final_data,
#             }
#         )

#         # Step 4: Return the same data to the API client
#         return Response(final_data, status=status.HTTP_201_CREATED)

#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(["POST"])
def SendMessageView(request, sender_id,reciver_id):
    print("K" * 50)
    key = str(reciver_id)
    print(key)
    
    serializer = MessageSerializer(data=request.data)
    if serializer.is_valid():
        message = serializer.save()

        # Step 1: Call external server using urllib
        external_data = {}
        url = f"https://mohammedmoh.pythonanywhere.com/user/{sender_id}/"
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

        # Step 3: Broadcast to WebSocket (Chat + Notification)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{message.room_name}",
            {
                "type": "chat_message",
                "message": final_data,
            }
        )

        async_to_sync(channel_layer.group_send)(
            f"notification_{key}",  # assuming NotificationConsumer listens to this
            {
                "type": "send_notification",  # your NotificationConsumer must handle this
                "notification": final_data,
            }
        )

        # Step 4: Return the same data to the API client
        return Response(final_data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
def SendMessageView2(request,user_id):
    print("K" * 50)
    print(user_id)
    key = str(user_id)
    print(key)
    serializer = MessageSerializer(data=request.data)
    if serializer.is_valid():
        message = serializer.save()
        headers = {'Content-Type': 'application/json'}
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
        sender_id = request.data.get("sender_id")


        if receiver_id:
            notification_message = f"You have a new message"
            notification_url = f"https://render-project1-qyk2.onrender.com/notification/send-save-notifications/{receiver_id}/{sender_id}"


            notification_data=json.dumps({
                "receiver": receiver_id,
                "sender": sender_id,
                "content": notification_message,
                "room_name": f"user_{receiver_id}"
            }).encode('utf-8')

            req2 = urllib.request.Request(notification_url, method='POST',headers=headers,data=notification_data)
            with urllib.request.urlopen(req2) as response:
                  if response.status == 201:
                    print("Notification sent:", response.status,)
                  else:
                    print("Notification couldn't send:", response.status,)
                
          
                 

        # Step 4: Return the same data to the API client
        return Response(final_data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)