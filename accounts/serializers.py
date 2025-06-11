from rest_framework import serializers
from .models import Profile
from django.contrib.auth import get_user_model

    
class LoginSerializer(serializers.Serializer):
    # Access fields from the related 'User' model
    email = serializers.EmailField(source='user.email', required=True)
    id = serializers.IntegerField(source='user.id',required=True)
    username = serializers.CharField(source='user.username', required=True)
    first_name = serializers.CharField(source='user.first_name', required=False, allow_blank=True)
    last_name = serializers.CharField(source='user.last_name', required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    weight = serializers.FloatField(required=False)
    height = serializers.FloatField(required=False)
    gender = serializers.CharField(required=False, allow_blank=True)
    goal = serializers.CharField(required=False, allow_blank=True)
    experianse_level = serializers.CharField(required=False, allow_blank=True)
    user_type = serializers.CharField(required=False, allow_blank=True) 

class ProfileSerializer(serializers.Serializer):
    # Access fields from the related 'User' model
    email = serializers.EmailField(source='user.email', required=True)
    id = serializers.IntegerField(source='user.id',required=True)
    username = serializers.CharField(source='user.username', required=True)
    first_name = serializers.CharField(source='user.first_name', required=False, allow_blank=True)
    last_name = serializers.CharField(source='user.last_name', required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    weight = serializers.FloatField(required=False)
    height = serializers.FloatField(required=False)
    gender = serializers.CharField(required=False, allow_blank=True)
    goal = serializers.CharField(required=False, allow_blank=True)
    experianse_level = serializers.CharField(required=False, allow_blank=True)
    user_type = serializers.CharField(required=False, allow_blank=True)
    

   
    

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    weight = serializers.FloatField(required=False)
    height = serializers.FloatField(required=False)
    gender = serializers.CharField(required=False, allow_blank=True)
    goal = serializers.CharField(required=False, allow_blank=True)
    experianse_level = serializers.CharField(required=False, allow_blank=True)
    user_type = serializers.CharField(required=False, allow_blank=True) 

    def validate_email(self, value):
        User = get_user_model()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def create(self, validated_data):
        # Extract user data
        username = validated_data.pop("username")
        email = validated_data.pop("email")
        password = validated_data.pop("password")
        
        if not username:
            raise serializers.ValidationError("Username is required.")
        if not email:
            raise serializers.ValidationError("Email is required.")
        if not password:
            raise serializers.ValidationError("Password is required.")
        
        # Create the user instance
        user_data = {
            "username": username,
            "email": email,
            "first_name": validated_data.pop("first_name", ""),
            "last_name": validated_data.pop("last_name", ""),
        }

        user = get_user_model()(**user_data)
        user.set_password(password)  # Hash the password
        user.save()
        
        # Create the profile instance
        profile = Profile.objects.create(user=user, **validated_data)

        return profile
    
    



