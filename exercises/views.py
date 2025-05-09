from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Exercise, ExerciseSchedule , Program
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
