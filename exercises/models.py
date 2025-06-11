from django.db import models
from accounts.models import Profile

class Exercise(models.Model):
    exercise_id = models.AutoField(primary_key=True)  # INT, PRIMARY KEY, AUTO_INCREMENT
    name = models.CharField(max_length=255)  # VARCHAR
    muscle_group = models.CharField(max_length=255)  # VARCHAR
    #video_url = models.URLField(blank=True, null=True)  # URL
    description = models.TextField(blank=True, null=True)  # TEXT

    def __str__(self):
        return self.name
    

class Program(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.TextField(max_length=500)
    coach = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name="Program_maker")
    trainer = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name="Program_assigned")
    exercises = models.ManyToManyField(Exercise, through='ExerciseSchedule', related_name="programs")
    created_at = models.DateTimeField(auto_now_add=True)


class ExerciseSchedule(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    day = models.CharField(max_length=10)
    sets = models.IntegerField()  
    reps = models.IntegerField()  

    class Meta:
        unique_together = ('exercise', 'program', 'day')  # لضمان عدم تكرار نفس التمرين في نفس اليوم

    def __str__(self):
        return f"{self.exercise.name} on {self.day} for {self.program.description} - Sets: {self.sets}, Reps: {self.reps}"