from rest_framework import serializers
from .models import Post,Comment
from accounts.serializers import ProfileSerializer

class PostSerializer(serializers.ModelSerializer):
    author = ProfileSerializer()
    like = ProfileSerializer(many=True)
    class Meta:
        model = Post
        fields = ['id', 'content', 'author','like','created_at']  

class CommentSerializer(serializers.ModelSerializer):
    writer = ProfileSerializer()
    class Meta:
        model = Comment
        fields = ['id','text', 'writer','time',]  