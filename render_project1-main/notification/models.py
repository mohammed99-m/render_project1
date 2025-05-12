from django.db import models

# Create your models here.
class Notification(models.Model):
    room_name = models.CharField(max_length=255)
    content = models.TextField()

