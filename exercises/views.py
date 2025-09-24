from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Exercise, ExerciseSchedule , Program, UserMessage
from .serializers import ExerciseSerializer , ProgramSerializer
from accounts.models import Profile


@api_view(["GET"])
def list_exercises(request):
    exercises = Exercise.objects.all()  
    serializer = ExerciseSerializer(exercises, many=True)  
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["GET"])
def search_exercises(request):
    query = request.query_params.get('q', None)  
    if query:
        exercises = Exercise.objects.filter(name__icontains=query)  
    else:
        exercises = Exercise.objects.all()  

    serializer = ExerciseSerializer(exercises, many=True)  
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def make_program(request,coach_id,trainer_id):
    coach = get_object_or_404(Profile,user__id=coach_id)
    print(coach.user.username)
    trainer = get_object_or_404(Profile,user__id=trainer_id)
    print(trainer.user.username)
    print("H"*50)
# استقبل البيانات المتعلقة بالأيام والتمارين
    days_exercises = request.data.get("days_exercises", [])
    print(days_exercises)
    program = Program.objects.filter(trainer=trainer).first()

    if program:
        return Response({"detail": "This User already got a trainning program"}, status=status.HTTP_400_BAD_REQUEST)
    
    print("H"*50)
    print("K"*50)
    if not days_exercises:
        return Response(
            {"detail": "At least one day of exercises must be provided"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
  
    program = Program.objects.create(
        coach=coach,
        trainer=trainer,
        description = request.data.get("description"),
    )

    for day_exercise in days_exercises:
        day = day_exercise.get("day")  
        sets = day_exercise.get("sets")  
        reps = day_exercise.get("reps")  
        exercises_ids = day_exercise.get("exercises", []) 

        if not exercises_ids:
             return Response({"detail": "Exercises must be provided for each day."}, status=status.HTTP_400_BAD_REQUEST)
        
        exercises = Exercise.objects.filter(exercise_id__in=exercises_ids)
        
        for exercise in exercises:
             ExerciseSchedule.objects.create(
                exercise=exercise,
                program=program,
                day=day,
                sets=sets,
                reps=reps
            )

    serialized_program = ProgramSerializer(program)
    return Response(serialized_program.data, status=status.HTTP_201_CREATED)

@api_view(["GET"])
def get_program(request, user_id):
    trainer = get_object_or_404(Profile, user__id=user_id)
    program = get_object_or_404(Program, trainer=trainer)

    schedules = ExerciseSchedule.objects.filter(program=program)
    exercises_with_days = []

    for schedule in schedules:
        exercise_info = {
            'day': schedule.day,
            'sets': schedule.sets,
            'reps' : schedule.reps,
            'exercise': ExerciseSerializer(schedule.exercise).data,
        }
        exercises_with_days.append(exercise_info)

    # إعداد البيانات للرد
    serialized_program = ProgramSerializer(program)
    response_data = serialized_program.data
    response_data['exercises'] = exercises_with_days  # إضافة التمارين مع الأيام

    return Response(response_data, status=status.HTTP_200_OK)

## NEED ADD 
@api_view(["DELETE"])
def delete_program(request,program_id,user_id):

    deleter = get_object_or_404(Profile,user__id=user_id)
    program = get_object_or_404(Program,id=program_id)

    if(program and (program.coach==deleter or program.trainer==deleter)):
            program.delete()
            return(Response("Program Deleted Succesfuly"))
    else:
           return(Response("no program with that info"))

#يحدث كامل البرنامج
@api_view(["Post"])
def update_program(request,coach_id,program_id):
    coach = get_object_or_404(Profile,user__id=coach_id)
    print(coach.user.username)
    program = get_object_or_404(Program,id=program_id)

    days_exercises = request.data.get("days_exercises", [])

    if not days_exercises:
        return Response({"detail": "Days and exercises must be provided."}, status=status.HTTP_400_BAD_REQUEST)
    

    if coach!=program.coach:
        print(program.coach.user.id)
        print(coach_id)
        return Response({"detail":"You Cant update on this program"})
    
    # حذف التمارين القديمة
    ExerciseSchedule.objects.filter(program=program).delete()

    for day_exercise in days_exercises:
        day = day_exercise.get("day")
        sets = day_exercise.get("sets")  
        reps = day_exercise.get("reps")
        exercises_ids = day_exercise.get("exercises", [])

        if not exercises_ids:
            return Response({"detail": f"At least one exercise must be provided for day {day}."}, status=status.HTTP_400_BAD_REQUEST)

        exercises = Exercise.objects.filter(exercise_id__in=exercises_ids)
        print("K"*50)

        if exercises.count() != len(exercises_ids):
            return Response(
                {"detail": "One or more exercises not found."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
        for exercise in exercises:
            ExerciseSchedule.objects.create(
                program=program,
                day=day,
                sets=sets, 
                reps=reps,
                exercise=exercise
            )
            
    serialized_program = ProgramSerializer(program)
    return Response(serialized_program.data, status=status.HTTP_200_OK)

#يحدث البرنامج من خلال التحديثات فقط ويبقي على الأيام التي لاتتغير
@api_view(["POST"])
def update_program_by_days(request, coach_id, program_id):
    coach = get_object_or_404(Profile, user__id=coach_id)
    program = get_object_or_404(Program, id=program_id)

    days_exercises = request.data.get("days_exercises", [])
    print(days_exercises)

    if not days_exercises:
        return Response({"detail": "Days and exercises must be provided."}, status=status.HTTP_400_BAD_REQUEST)

    if coach != program.coach:
        return Response({"detail": "You can't update this program."})
  
    existing_days = list(ExerciseSchedule.objects.filter(program=program).values_list('day', flat=True))
    print(existing_days)

    for day_exercise in days_exercises:
        day = day_exercise.get("day")
        sets = day_exercise.get("sets")
        reps = day_exercise.get("reps")
        exercises_ids = day_exercise.get("exercises", [])
        print( {day})

        if not exercises_ids:
            return Response({"detail": f"At least one exercise must be provided for day {day}."}, status=status.HTTP_400_BAD_REQUEST)
        print(f"dd: {day},ex {existing_days}")

        exercises = Exercise.objects.filter(exercise_id__in=exercises_ids)
        
        if exercises.count() != len(exercises_ids):
            return Response({"detail": "One or more exercises not found."}, status=status.HTTP_400_BAD_REQUEST)
        
        #اذا كان اليوم موجود في البرنامج يتم تحديثه كاملا حيث يحذف التمارين السابقة
        if str(day) in existing_days:
            print(f"Deleting exercises for {day}")
            ExerciseSchedule.objects.filter(program=program, day=day).delete()
            

        # نضيف التمارين واليوم 
        for exercise in exercises:
            ExerciseSchedule.objects.create(
                program=program,
                day=day,
                sets=sets, 
                reps=reps ,
                exercise=exercise
                )
    
    program.refresh_from_db()    
    serialized_program = ProgramSerializer(program)
    
    return Response(serialized_program.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_coach_programs(request,coach_id):
    coach = get_object_or_404(Profile,user__id=coach_id)
    programs = Program.objects.filter(coach=coach)

    serializer = ProgramSerializer(programs,many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["GET"])
def get_exercises_by_muscle(request):
    query = request.query_params.get('q', None)  
    if query:
        exercises = Exercise.objects.filter(muscle_group__icontains=query)  
    else:
        exercises = Exercise.objects.all()  

    serializer = ExerciseSerializer(exercises, many=True)  
    return Response(serializer.data, status=status.HTTP_200_OK)

from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
import cloudinary.uploader
import urllib.request
import json

@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def add_exercise_with_video(request):
    # Get fields from request
    name = request.data.get("name")
    muscle_group = request.data.get("muscle_group")
    description = request.data.get("description")
    video = request.FILES.get("video")  # optional

    video_url = None
    if video:
        try:
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                video,
                resource_type="video"
            )
            video_url = upload_result.get("secure_url")
        except Exception as e:
            return Response({"error": f"Video upload failed: {str(e)}"}, status=500)

    # Prepare data to send (video_url may be None)
    data_to_send = {
        "name": name,
        "muscle_group": muscle_group,
        "description": description,
        "video_url": video_url  # can be None
    }

    # Send POST request to external server
    try:
        url = "https://mohammedmoh.pythonanywhere.com/exercises/add-exercise-with-video/"
        headers = {"Content-Type": "application/json"}
        data = json.dumps(data_to_send).encode("utf-8")

        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req) as response:
            external_response = response.read().decode("utf-8")
    except Exception as e:
        return Response({
            "request_data": data_to_send,
            "external_error": str(e)
        }, status=status.HTTP_201_CREATED)

    return Response({
        "request_data": data_to_send,
        "external_response": external_response
    }, status=status.HTTP_201_CREATED)


#########################################################################################################

from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
import cloudinary.uploader
import urllib.request
import uuid
import mimetypes

@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def add_service_with_media(request):
    name = request.data.get("name")
    content = request.data.get("content")
    date = request.data.get("date")
    image = request.FILES.get("image")
    video = request.FILES.get("video")

    # رفع الصور والفيديوهات إلى Cloudinary
    image_url = None
    video_url = None

    try:
        if image:
            upload_image = cloudinary.uploader.upload(image, resource_type="image")
            image_url = upload_image.get("secure_url")
        if video:
            upload_video = cloudinary.uploader.upload(video, resource_type="video")
            video_url = upload_video.get("secure_url")
    except Exception as e:
        return Response({"error": f"Media upload failed: {str(e)}"}, status=500)

    # تجهيز البيانات
    fields = {
        "name": name,
        "content": content,
        "date": date,
        "image_url": image_url or "",
        "video_url": video_url or ""
    }


    try:
        url = "https://mohammed229.pythonanywhere.com/main/addservice_with_video/"
        headers = {"Content-Type": "application/json"}
        data = json.dumps(fields).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req) as response:
            external_response = response.read().decode("utf-8")
    except Exception as e:
        return Response({
            "request_data": fields,
            "external_error": str(e)
        }, status=status.HTTP_201_CREATED)

    return Response({
        "request_data": fields,
        "external_response": external_response
    
    }, status=status.HTTP_201_CREATED)

from django.conf import settings
from django.core.mail import EmailMessage, BadHeaderError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.html import escape
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
import json
import re
import logging
from django.conf import settings
from django.core.mail import EmailMessage, BadHeaderError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.html import escape
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie

logger = logging.getLogger(__name__)

HEADER_INJECTION_RE = re.compile(r'[\r\n]')
MAX_NAME_LEN = 120
MAX_EMAIL_LEN = 254
MAX_MESSAGE_LEN = 5000
from django.views.decorators.csrf import csrf_protect
@csrf_protect
def api_send_message4(request):
    """
    - POST (JSON/AJAX): يعالج البيانات القادمة من الموبايل أو الواجهة الأمامية
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    data = {
        "user_name": payload.get("user_name", ""),
        "user_email": payload.get("user_email", ""),
        "message": payload.get("message", ""),
    }
    return _process_contact_data(request, data)
def _process_contact_data(request, data):
    """
    دالة مشتركة: تحقق من المدخلات + تخزين + إرسال إيميل
    """
    raw_name = (data.get("user_name") or "").strip()
    raw_email = (data.get("user_email") or "").strip()
    raw_message = (data.get("message") or "").strip()

    if not raw_message:
        return _response_by_request_type(request, {"error": "Message cannot be empty."}, status=400)

    if len(raw_name) > MAX_NAME_LEN or len(raw_email) > MAX_EMAIL_LEN or len(raw_message) > MAX_MESSAGE_LEN:
        return _response_by_request_type(request, {"error": "One of the fields is too long."}, status=400)

    for val in (raw_name, raw_email):
        if HEADER_INJECTION_RE.search(val):
            return _response_by_request_type(request, {"error": "Invalid characters in input."}, status=400)

    try:
        validate_email(raw_email)
    except ValidationError:
        return _response_by_request_type(request, {"error": "Invalid email address."}, status=400)

    safe_name = escape(raw_name)
    safe_message = escape(raw_message)

    try:
        UserMessage.objects.create(
            user_name=safe_name,
            user_email=raw_email,
            message=safe_message
        )
    except Exception as e:
        logger.exception("Failed to save UserMessage")
        return _response_by_request_type(request, {"error": "Failed to save message."}, status=500)

    subject = f"رسالة من {raw_name or 'مستخدم مجهول'}"
    full_message = f"رسالة من: {raw_name} <{raw_email}>\n\n{raw_message}"

    try:
        email = EmailMessage(
              subject=subject,
              body=full_message,
              from_email=settings.EMAIL_HOST_USER,   # البريد المرسل منه
              to=[settings.ADMIN_EMAIL],             # البريد المستلم (حدد في settings.py)
              reply_to=[raw_email],                  # البريد الذي يرد عليه
)
        email.send(fail_silently=False)
    except BadHeaderError:
        return _response_by_request_type(request, {"error": "Invalid header found."}, status=400)
    except Exception:
        logger.exception("Failed to send email")
        return _response_by_request_type(request, {"error": "Failed to send email."}, status=500)

    return _response_by_request_type(request, {"status": "Message sent successfully."}, status=200)


def _response_by_request_type(request, payload, status=200):
    """
    يرجع JSON لو الطلب AJAX/JSON
    ويرجع HTML لو كان من فورم عادي
    """
    if request.content_type == "application/json" or "application/json" in request.META.get("HTTP_ACCEPT", ""):
        return JsonResponse(payload, status=status)

    if status == 200:
        return render(request, "contact.html", {"success": payload.get("status", "")})
    else:
        return render(request, "contact.html", {"error": payload.get("error", "")}, status=status)

