from rest_framework import serializers
from .models import DefUser

class NameSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefUser
        fields = ['name']