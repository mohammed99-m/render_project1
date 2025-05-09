from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Post, Profile,Comment
from .serializers import PostSerializer,CommentSerializer
from accounts.serializers import ProfileSerializer
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
@api_view(['POST'])
def add_post(request,author_id):
    content = request.data.get('content')  

    try:
       
        profile = get_object_or_404(Profile,user_id=author_id)
    except Profile.DoesNotExist:
        return Response({'error': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

  
    serializer = ProfileSerializer(profile)
    post_data = {
        'content': content,
        'author': serializer.data,  
    }
    print(post_data)
    post = Post(author=profile,content= content)
    serializer = PostSerializer(post)
    print(post.author.user.id)
    post.save()  
    return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_all_posts(request):
    posts = Post.objects.all()
    serializer = PostSerializer(posts,many=True)

    return(Response(serializer.data))


@api_view(['GET'])
def get_someone_posts(request,user_id):
    profile = Profile.objects.get(user__id=user_id)
    posts = Post.objects.filter(author=profile)
    serializer = PostSerializer(posts,many=True)

    return Response(serializer.data)


@api_view(['POST'])
def like_on_post(request, post_id, user_id):
    try:
        post = Post.objects.get(id=post_id)
        profile = Profile.objects.get(user__id=user_id)
    except Post.DoesNotExist:
        return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)
    except Profile.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    if profile in post.like.all():  
        post.like.remove(profile)
        return Response({"message": "You unliked the post."})
    else:
        post.like.add(profile) 
        return Response({"message": "You liked the post."})


@api_view(['post'])
def add_comment(request,post_id,user_id):
    try:
        
        profile = Profile.objects.get(user__id=user_id)
    except Profile.DoesNotExist:
        return Response({'error': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)
    try:
       
        post = Post.objects.get(id=post_id)
    except Profile.DoesNotExist:
        return Response({'error': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    comment = Comment(writer=profile,post=post,text=request.data['text'])
    comment.save()
    return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_comments_on_post(request,post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"error":"post not found."},status=status.HTTP_404_NOT_FOUND) 

    comment = Comment.objects.filter(post=post)   
    serializer = CommentSerializer(comment,many=True)

    return Response(serializer.data)