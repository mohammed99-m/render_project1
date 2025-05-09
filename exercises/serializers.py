from rest_framework import serializers
from .models import Exercise, ExerciseSchedule, Program
from accounts.serializers import ProfileSerializer

class ExerciseSerializer(serializers.Serializer):
    exercise_id = serializers.IntegerField(read_only=True) 
    name = serializers.CharField(max_length=255, required=True) 
    muscle_group = serializers.CharField(max_length=255, required=True)  
    #video_url = serializers.URLField(required=False, allow_blank=True) 
    description = serializers.CharField(required=False, allow_blank=True) 

class ProgramSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    description = serializers.CharField(max_length = 500 , required=True)
    coach = ProfileSerializer()
    trainer = ProfileSerializer()
    exercises = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)

    def get_exercises(self, obj):
        schedules = ExerciseSchedule.objects.filter(program=obj)
        return ExerciseScheduleSerializer(schedules, many=True).data

class ExerciseScheduleSerializer(serializers.ModelSerializer):
    exercise = serializers.PrimaryKeyRelatedField(queryset=Exercise.objects.all())
    program = serializers.PrimaryKeyRelatedField(queryset=Program.objects.all())

    class Meta:
        model = ExerciseSchedule
        fields = ['exercise', 'program', 'day' ,'sets', 'reps']

    