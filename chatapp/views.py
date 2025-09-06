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
            "external_result": external_data,
            "room_id":message.room_id
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

#يجب اضافة المرسل والمستقبل ضمن جسم تابع ارسال الرسالة 
        receiver_id = request.data.get("receiver_id")
        sender_id = request.data.get("sender_id")
        
        if sender_id and receiver_id:
            try:
                #save-message يحفظ الرسالة المرسلة على السيرفر الرئيسي باستخدام التابع
                save_url = "https://mohammedmoh.pythonanywhere.com/chatapp/save-message/"
                save_data = json.dumps({
                    "sender": sender_id,
                    "receiver": receiver_id,
                    "room_name": message.room_name,
                    "room_id" :  message.room_id,
                    "content": message.content,
                }).encode('utf-8')

                save_request = urllib.request.Request(
                    save_url,
                    method='POST',
                    data=save_data,
                    headers=headers
                )

                with urllib.request.urlopen(save_request) as save_response:
                    if save_response.status == 201:
                        print("Message saved to main server.")
                    else:
                        print("Failed to save message:", save_response.status)
            except Exception as e:
                print("Error saving message to main server:", str(e))
        else:
            print("Missing sender_id or receiver_id, message not saved to main server.")
#يرسل الاشعار للمستقبل ويحفظها في الداتا بيز الرئيسية
        if receiver_id:
            notification_message = f"You have a new message"
            notification_url = f"https://web-production-830a0.up.railway.app/notification/send-save-notifications/{receiver_id}/{sender_id}"


            notification_data=json.dumps({
                "content": notification_message,
                "user_id": receiver_id,
                "room_name": f"{receiver_id}",
                "room_id":message.room_id
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