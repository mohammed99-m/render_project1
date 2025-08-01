import json
from rest_framework.response import Response
from rest_framework.decorators import api_view
import urllib
from .serializers import RegisterSerializer,LoginSerializer
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Profile
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import User
from exercises.models import Program
from health.models import DietPlan

@api_view(["POST"])
def sign_up(request):

    User = get_user_model()
    if User.objects.filter(username=request.data['username']).exists():
        return Response({"message": "this User name already Exist"}, status=status.HTTP_404_NOT_FOUND)
    
    profile_serializer = RegisterSerializer(data=request.data)
    if profile_serializer.is_valid():

        # Save the serializer to create the Profile instance
        profile = profile_serializer.save()

        # Access the user instance associated with the profile
        user = profile.user
        
        # Generate a token for the user
        #token, created = Token.objects.get_or_create(user=user)
        acces_token = AccessToken.for_user(user)

        response_data = {
            #"token": token.key,
            "token":str(acces_token),
            "user": {
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": profile.phone,
                "weight": profile.weight,
                "height": profile.height,
                "id": user.id,
                "gender":profile.gender,
                "goal": profile.goal,
                "experianse_level" :profile.experianse_level,
                "user_type":profile.user_type
            },
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    # Return errors if the serializer is invalid
    if(profile_serializer.errors.get('email')!=None):
      return Response({"message": "This Email already exist"},status=status.HTTP_404_NOT_FOUND)
    if(profile_serializer.errors.get('password')!=None):
      return Response({"message": "add password"}, status=status.HTTP_404_NOT_FOUND)
    return Response({"message": "something get wrong"}, status=status.HTTP_404_NOT_FOUND)



@api_view(["POST"])
def login(request):
    try:
        # Get the user by username and handle errors if the user does not exist
        user = get_object_or_404(get_user_model(), username=request.data['username'])
        
        # Check the password
        if not user.check_password(request.data['password']):
            return Response({"message": "Invalid credentials"}, status=status.HTTP_404_NOT_FOUND)

        # Get or create token for the user
        #token, created = Token.objects.get_or_create(user=user)
        acces_token = AccessToken.for_user(user)


        # Retrieve the profile related to the user
        profile = get_object_or_404(Profile, user=user)

        # Serialize the profile data, ensuring we access fields from the related 'User' model
        serializer = LoginSerializer(instance=profile)

        # Return the token and serialized profile data
        #return Response({"token": token.key, "user": serializer.data})
        return Response({"token": str(acces_token), "user": serializer.data})

    except KeyError as e:
        return Response({"message": f"Missing field: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import RegisterSerializer , LoginSerializer

@api_view(["GET"])
@authentication_classes([JWTAuthentication]) 
@permission_classes([IsAuthenticated])
def test_token(request):
   
    user = request.user
    profile = user.profile  
    serializer = LoginSerializer(profile)
    
    return Response({
        "user": serializer.data
    })


@api_view(["DELETE"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_account(request):
    user = request.user

  
    profile = get_object_or_404(Profile, user=user)

    profile.delete()

    user.delete()

    return Response({"message": "Account deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from .models import Profile

@api_view(["PUT"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_profile_field(request):
    ## نحصل على المستخدم الافتراضي المتعلق بالتوكين المرسل برسالة الطلب 
    user = request.user 
    ## نحصل على البروفايل للمستخدم المحدد
    profile = user.profile
  
    ## نخزن البيانات القادمة في جسم الطلب ونصل على القيمة عن طريق المفتاح
    field_name = request.data.get("field")
    field_value = request.data.get("value")
    ## في حال كانت البيانات خاطئة في جسم الطلب 
    if not field_name:
        return Response({"message": "Field name is required."}, status=status.HTTP_400_BAD_REQUEST)

    ## نحصل على اسماء جميع الحثول في البروفايل و المستخدم الافتراضي 
    profile_fields = [field.name for field in Profile._meta.get_fields()]
    user_fields = [field.name for field in User._meta.get_fields()]

    ##  في حال كان المراد تعديله هو الايميل 
    if field_name == "email":
        ##  التحقق من عدم تكرار الايميل او ادخال ايميل خاطئ
        if not field_value or not isinstance(field_value, str) or "@" not in field_value:
            return Response(
                {"message": "Invalid email address."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ## التحقق من عدم وجود الايميل مسبقا
        if User.objects.filter(email=field_value).exclude(id=user.id).exists():
            return Response(
                {"message": "This email is already in use by another account."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ## في حال كان الايميل ممكن التعديل نخزن الايميل الجديد
        user.email = field_value
        user.save()
        return Response(
            {"message": "Email updated successfully.", "value": field_value},
            status=status.HTTP_200_OK,
        )
    ## في حال كان المراد تغييره هو اسم المستخدم
    if field_name == "username":
        ## الاسم موجود مسبقا 
        if User.objects.filter(username=field_value).exclude(id=user.id).exists():
            return Response(
                {"message": "This username Is already in use by another account"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ## ان كان الاسم ممكن نخزن الاسم الجديد
        user.username = field_value
        user.save()
        return Response(
            {"message": "UserName updated successfully.", "value": field_value},
            status=status.HTTP_200_OK,
        )
    ## في حال كان المراد تغيير هو رقم الهاتف
    if field_name == "phone":
        ## التاكد انا الرقم غير موجود مسبقا 
        if Profile.objects.filter(phone=field_value).exclude(user=user).exists():
            return Response(
                {"message": "This phone is already in use by another account."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ## حفظ رقم الهاتف الجديد
        profile.phone = field_value
        profile.save()
        return Response(
            {"message": "Phone updated successfully.", "value": field_value},
            status=status.HTTP_200_OK,
        )
     ##  في حال تعديل خانة اخرى وكانت ضمن حقول المستخدم الافتراضي
    if field_name in user_fields:
        setattr(user, field_name, field_value)
        user.save()
        return Response(
            {"message": f"'{field_name}' updated successfully", "value": field_value},
            status=status.HTTP_200_OK,
        )

    ## في حال تعديل خانة اخرى و كانت ضمن حقول البروفايل
    elif field_name in profile_fields:
        setattr(profile, field_name, field_value)
        profile.save()
        return Response(
            {"message": f"'{field_name}' updated successfully", "value": field_value},
            status=status.HTTP_200_OK,
        )
    ## في حال ارسال مفتاح خاطئ
    return Response(
        {"message": f"Field '{field_name}' does not exist."},
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(['GET'])
def get_users(request):
    # جلب جميع البروفايلات
    profile = Profile.objects.all()
    #باستخدام السيريالايزرjsonتحويل البيانات الى 
    serializer = LoginSerializer(profile,many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_coaches(request):
    # جلب جميع المدربين
    profile = Profile.objects.filter(user_type="coach")
    # json تحويل البيانات الى
    serializer = LoginSerializer(profile,many=True)
    return Response(serializer.data)
    


@api_view(["GET"])
# جلب مستخد محدد
def get_specific_user(request,user_id):
    ##  المحدد id جلب المستخدم ذو ال
    user = get_object_or_404(User,id=user_id)
    ## جلب البروفايل الموافق للمستخد الافتراضي الصحيح
    profile = Profile.objects.get(user = user)
    ##json تحويل البيانات
    serializer = LoginSerializer(profile)
    return Response(serializer.data)


@api_view(['GET'])
## جلب المتدربين الخاصين بمدرب معين
def get_trainers(request, coach_id):
    try:
        ## البروفايل الخاص بمدرب معين
        profile = Profile.objects.get(user__id=coach_id)
        ##json  نمرر جميع المستخدمين الموجودين بمصفوفة المتدربين لدى المدرب و نحولها الى
        ## استخدمنا السيريالايزير الخاص بتسجيل الدخول بكفي و بوفي 
        serializer = LoginSerializer(profile.trainers.all(), many=True)
        
        return Response(serializer.data, status=200)
    #الممرر id اذا كان مافي بروفايل لهاد ال 
    except Profile.DoesNotExist:
        return Response({"message": "Profile not found"}, status=404)
    
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json
import urllib.request
import urllib.error

@api_view(['POST'])
def send_join_request22(request, trainer_id, coach_id):
    send_join_request_url = f"https://mohammedmoh.pythonanywhere.com/sendjoinrequest/{trainer_id}/{coach_id}/"
    notification_url = "https://mohammedmoh.pythonanywhere.com/notifications/save-notification/"
    websocket_notification_url = f"https://render-project1-qyk2.onrender.com/notification/send-save-notifications/{coach_id}/{trainer_id}"

    headers = {'Content-Type': 'application/json'}

    try:
        # Step 1: Send join request
        join_request = urllib.request.Request(send_join_request_url, method='POST', headers=headers)
        with urllib.request.urlopen(join_request) as response:
            if response.status != 201:
                return Response({"message": "فشل في إرسال طلب الانضمام"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            join_result = json.loads(response.read().decode())
            if join_result.get('message') != 'Join request sent successfully':
                return Response({"message": join_result.get('message')}, status=status.HTTP_200_OK)

        # Step 2: Prepare notification data
        content = f"{request.data.get('name')} sent you a join request"
        room_name = str(coach_id)
        notification_data = {
            'receiver': coach_id,
            'sender': trainer_id,
            'content': content,
            'room_name': room_name,
        }
        encoded_data = json.dumps(notification_data).encode('utf-8')

        # Step 3: Send real-time & push notification
        notify_request = urllib.request.Request(
            websocket_notification_url,
            method='POST',
            headers=headers,
            data=encoded_data
        )
        with urllib.request.urlopen(notify_request) as notify_response:
            notify_response_text = notify_response.read().decode('utf-8')
            print("✅ Notification sent:", notify_response_text)

        # Step 4: Save notification to main server
        save_request = urllib.request.Request(
            notification_url,
            method='POST',
            headers=headers,
            data=encoded_data
        )
        with urllib.request.urlopen(save_request) as save_response:
            save_result = save_response.read().decode('utf-8')
            print("✅ Notification saved:", save_result)

        return Response(
            {"message": "✅ تم إرسال طلب الانضمام والإشعار بنجاح"},
            status=status.HTTP_201_CREATED
        )

    except urllib.error.HTTPError as e:
        error_detail = e.read().decode()
        return Response(
            {"error": str(e), "details": error_detail},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import urllib.request
import json

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import urllib.request
import json
import time

@api_view(['POST'])
def send_join_request(request, trainer_id, coach_id):
    send_join_request_url = f"https://mohammedmoh.pythonanywhere.com/sendjoinrequest/{trainer_id}/{coach_id}/"
    send_notification_url = f"https://render-project1-qyk2.onrender.com/notification/send-save-notifications/{coach_id}/{trainer_id}"

    headers = {'Content-Type': 'application/json'}
    result_response = {
        "join_request": None,
        "notification_status": None,
        "errors": []
    }

    # 1. إرسال طلب الانضمام
    try:
        join_req = urllib.request.Request(send_join_request_url, method='POST', headers=headers)
        with urllib.request.urlopen(join_req) as response:
            if response.status == 201:
                result_response["join_request"] = "Join request sent successfully"
            else:
                result_response["join_request"] = "Failed to send join request"
                return Response(result_response, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        result_response["errors"].append(f"Join request error: {str(e)}")
        return Response(result_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ✅ تأخير بسيط للسماح بانتشار البيانات
    time.sleep(2)

    # 2. تجهيز بيانات الإشعار
    name = request.data.get('name', 'Someone')
    content = request.data.get('content', f"{name} sent you a join request")
    room_name = str(coach_id)

    notification_data = json.dumps({
        'content': content,
        'room_name': room_name
    }).encode('utf-8')
    
    # 3. إرسال الإشعار
    try:
        notif_req = urllib.request.Request(send_notification_url, method='POST', headers=headers, data=notification_data)
        with urllib.request.urlopen(notif_req) as notif_response:
            notif_data = notif_response.read().decode('utf-8')
            result_response["notification_status"] = "Notification sent and saved"
            result_response["notification_response"] = json.loads(notif_data)
            return Response(result_response, status=status.HTTP_201_CREATED)

    except urllib.error.HTTPError as e:
        error_content = e.read().decode()
        result_response["notification_status"] = "Notification failed"
        result_response["errors"].append(f"HTTPError: {str(e)} - {error_content}")
        return Response(result_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        result_response["notification_status"] = "Notification failed"
        result_response["errors"].append(f"Exception: {str(e)}")
        return Response(result_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#######
# @api_view(['POST'])
# def send_join_request(request,trainer_id,coach_id):
#     send_join_request_url = f"https://mohammedmoh.pythonanywhere.com/sendjoinrequest/{trainer_id}/{coach_id}/"
#     send_notification_url = f"https://render-project1-qyk2.onrender.com/notification/send-notifications-push-updated/{coach_id}/"
#         # Send POST request to like the post
#     headers = {'Content-Type': 'application/json'}
#     req = urllib.request.Request(send_join_request_url, method='POST',headers=headers)
#     with urllib.request.urlopen(req) as response:
#             print(response.status)
#             print("H"*50)
#             print(send_notification_url)
#             if response.status == 201:
#                 data = response.read().decode('utf-8')
#                 result = json.loads(data)
#                 action = result.get('message')
#                 if action == 'Join request sent successfully':
#                     print("you send the request succesfuly")

#                     # Send GET request to notification URL
#                     notification_data = json.dumps({
#                         'content': f"{request.data['name']} send you a join request",
#                         'room_name':f'{coach_id}',
#                       }).encode('utf-8')
#                     try:
                        
#                         req2 = urllib.request.Request(send_notification_url, method='POST',headers=headers,data=notification_data)
#                         with urllib.request.urlopen(req2) as notify_response:
#                             print(notify_response.status)
#                             if notify_response.status == 201:
#                                 return Response(
#                                     {"message": "You send the request succesfuly and notification sent."},
#                                     status=status.HTTP_201_CREATED
#                                 )
#                             else:
#                                 return Response(
#                                     {"message": "You send the request succesfuly, but failed to send notification."},
#                                     status=status.HTTP_500_INTERNAL_SERVER_ERROR
#                                 )
#                     except urllib.error.HTTPError as e:
#                         return Response(
#                             {"message": "You send the request succesfuly, but failed to send notification.", "error": str(e)},
#                             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#                         )

#                 else:
#                     return Response({"message": f"{action}"}, status=status.HTTP_200_OK)

#             else:
#                 return Response({"message": f"Failed to You send the request"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
 
from .models import JoinRequest
@api_view(['POST'])
def response_to_join_request(request,request_id,coach_id,trainer_id):
    send_join_request_url = f"https://mohammedmoh.pythonanywhere.com/responsetojoinrequest/{coach_id}/{request_id}/"
    send_notification_url = f"https://render-project1-qyk2.onrender.com/notification/send-save-notifications/{trainer_id}/{coach_id}"
        # Send POST request to like the post
    headers = {'Content-Type': 'application/json'}
    join_request_data = json.dumps({"action": request.data['action']}).encode('utf-8')
    req = urllib.request.Request(send_join_request_url, method='POST',headers=headers,data=join_request_data)
    with urllib.request.urlopen(req) as response:
            print(response.status)
            print("H"*50)
            print(send_notification_url)
            if response.status == 201:
                data = response.read().decode('utf-8')
                result = json.loads(data)
                action = result.get('message')
                if action == 'Join request accepted' or action =='Join request rejected':
                    message =""
                    if action == 'Join request accepted':
                        message = "Accept"
                    else:
                        message = "Reject"
                    # Send GET request to notification URL
                    notification_data = json.dumps({
                        'content': f"coach {request.data['name']} {message} your join request",
                        'room_name':f'{trainer_id}',
                      }).encode('utf-8')
                    try:
                        
                        req2 = urllib.request.Request(send_notification_url, method='POST',headers=headers,data=notification_data)
                        with urllib.request.urlopen(req2) as notify_response:
                            print(notify_response.status)
                            if notify_response.status == 201:
                                return Response(
                                    {"message": f"{action} and notification sent."},
                                    status=status.HTTP_201_CREATED
                                )
                            else:
                                return Response(
                                    {"message": f"{action}, but failed to send notification."},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                                )
                    except urllib.error.HTTPError as e:
                        return Response(
                            {"message": f"{action}, but failed to send notification.", "error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )

                else:
                    return Response({"message": f"{action}"}, status=status.HTTP_200_OK)

            else:
                return Response({"message": f"Failed to You send the request"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
@api_view(['GET'])
# جلب جميع طلبات الانضمام الخاصة بمدرب معين
def get_join_requests(request, coach_id):
    try:

        coach_profile = Profile.objects.get(user__id=coach_id)

        # جلب جميع الطلبات المنتظرة الخاصة بالمدرب المحدد
        requests = JoinRequest.objects.filter(coach=coach_profile, status='Pending')
        ## ارسال بعض المعلومات الخاصة بطلبات الانضمام
        data = [
            {
                "id": req.id,
                "user_id": req.trainer.user.id,
                "trainer_name": req.trainer.user.username,
                "created_at": req.created_at
            }
            for req in requests
        ]
        return Response(data, status=200)
    except Profile.DoesNotExist:
        return Response({"message": "Coach Profile not found"}, status=404)
    
@api_view(["GET"])
def return_experince_level(request):
    data =  [
          "beginner",
          "intermediate",
          "advanced"
        ]
      
    return Response(data,status=200)

@api_view(["GET"])
def return_goals(request):
    data = [
        "lose_weight",
        "build_muscle",
        "endurance"
        ]
    
    return Response(data,status=200)

@api_view(['GET'])
def get_request_status(request, trainer_id):
    try:

        trainer_profile = Profile.objects.get(user__id=trainer_id)

        requests = JoinRequest.objects.filter(trainer=trainer_profile)

        data = [
            {
                "id": req.id,
                "coach_id": req.coach.user.id,
                "trainer_id":req.trainer.user.id,
                "coach_name": req.coach.user.username,
                "trainer_name":req.trainer.user.username,
                "status":req.status,
                "created_at": req.created_at
            }
            for req in requests
        ]
        return Response(data, status=200)
    except Profile.DoesNotExist:
        return Response({"error": "Trainner Profile not found"}, status=404)
    

@api_view(['GET'])
## جلب المتدربين الخاصين بمدرب معين
def get_trainer_info(request,trainer_id,coach_id):
    try:
        ## البروفايل الخاص بمدرب معين
        coach = get_object_or_404(Profile,user__id=coach_id)
        trainer = get_object_or_404(Profile,user__id=trainer_id)
        joinRequest = get_object_or_404(JoinRequest,trainer=trainer,coach=coach)
        
        no_program = True
        no_dietPlan = True
        try:
          Program.objects.get(trainer=trainer,coach=coach)
        except Program.DoesNotExist:
            no_program = False

        try:
            DietPlan.objects.get(trainer=trainer,coach=coach)
        except DietPlan.DoesNotExist:
             no_dietPlan = False

        data = {
            "join_status":joinRequest.status,
            "program_status":no_program,
            "dietPlan_status":no_dietPlan
        }
        
        return Response(data, status=200)
    #الممرر id اذا كان مافي بروفايل لهاد ال 
    except Profile.DoesNotExist:
        return Response({"error": "Profile not found"}, status=404)
    