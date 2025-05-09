from rest_framework.response import Response
from rest_framework.decorators import api_view
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
    


from .models import JoinRequest
@api_view(['POST'])
def send_join_request(request, user_id, coach_id):
    try:
        ##المرسل id البروفايل الخاص بالمتدرب من ال 
        trainer_profile = Profile.objects.get(user__id=user_id)
        ##المرسل id البروفايل الخاص بالمدرب من ال 
        coach_profile = Profile.objects.get(user__id=coach_id)

        # اذا الطلب الردي مبعوت
        if JoinRequest.objects.filter(trainer=trainer_profile, coach=coach_profile, status='Pending').exists():
            return Response({"message": "a pending request already exist"}, status=400)
        
        if trainer_profile.id in [trainer.id for trainer in coach_profile.trainers.all()]:
              return Response({"message": "You are already joined with that coach"}, status=400)

        #  والا ننشئ خانة جديدة في جدول الطلبات
        JoinRequest.objects.create(trainer=trainer_profile, coach=coach_profile)
        return Response({"message": "Join request sent successfully"}, status=201)
    # في حال مافي متدرب او مدرب موافق للايدي المبعوت
    except Profile.DoesNotExist:
        return Response({"message": "User or Coach Profile not found!"}, status=404)
    

 
@api_view(['POST'])
## الرد على الطلب بموافقة او رفض
def respond_to_join_request(request, coach_id, request_id):
    try:
        ## جلب المدرب و طلب الارسال من الجداول
        coach_profile = Profile.objects.get(user__id=coach_id)
        join_request = JoinRequest.objects.get(id=request_id, coach=coach_profile)

        # request انشاء متحول بقيمة الرد القادم من ال 
        action = request.data.get('action')
        ## هون اذا كنا باعتين شي غلط غير الرفض و القبول
        if action not in ['Accept', 'Reject']:
            return Response({"message": "Invalid action. Use 'Accept' or 'Reject'."}, status=400)
        
        # حالة القبول 
        if action == 'Accept':
            #منضيف المستخدم الموجود ضمن طلب الانضمام لمصفوفة المتدربين الخاصين بهذا المدرب
            coach_profile.trainers.add(join_request.trainer)
            #هون صارت حالة الطلب هي مقبول
            join_request.status = 'Accepted'
            join_request.save()
            return Response({"message": "Join request accepted"}, status=200)
        # حالة الرفض 
        elif action == 'Reject':
            join_request.status = 'Rejected'
            join_request.save()
            return Response({"message": "Join request rejected"}, status=200)
    ## حالات الفشل
    except Profile.DoesNotExist:
        return Response({"message": "Coach Profile not found"}, status=404)
    except JoinRequest.DoesNotExist:
        return Response({"message": "Join request not found"}, status=404)


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