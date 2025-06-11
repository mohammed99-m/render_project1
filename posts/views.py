import json
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import urllib
from .models import Post, Profile,Comment
from .serializers import PostSerializer,CommentSerializer
from accounts.serializers import ProfileSerializer
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from notification.consumers import Notification

# @api_view(['POST'])
# def add_post(request,author_id):
#     content = request.data.get('content')  
#     add_post_url = f"https://mohammedmoh.pythonanywhere.com/posts/like/{post_id}/"
#         # Send POST request to like the post
#     headers = {'Content-Type': 'application/json'}
#     req = urllib.request.Request(like_post_url, method='POST',headers=headers)
#     with urllib.request.urlopen(req) as response:
#             print(req.data)
#             print(response.status)
#             print("H"*5)
#             print(like_post_url)
#             if response.status == 200:
#                 data = response.read().decode('utf-8')
#                 result = json.loads(data)
#                 action = result.get('message')
#                 if action == 'like':
#                     print("You liked the post.")

#                     # Send GET request to notification URL
#                     notification_data = json.dumps({
#                         'content': f"{request.data['name']} like your post",
#                         'room_name':f'{author_id}',
#                       }).encode('utf-8')
#                     try:
                        
#                         req2 = urllib.request.Request(send_notification_url, method='POST',headers=headers,data=notification_data)
#                         with urllib.request.urlopen(req2) as notify_response:
#                             print(notify_response.status)
#                             if notify_response.status == 201:
#                                 return Response(
#                                     {"message": "You liked the post and notification sent."},
#                                     status=status.HTTP_201_CREATED
#                                 )
#                             else:
#                                 return Response(
#                                     {"message": "You liked the post, but failed to send notification."},
#                                     status=status.HTTP_500_INTERNAL_SERVER_ERROR
#                                 )
#                     except urllib.error.HTTPError as e:
#                         return Response(
#                             {"message": "You liked the post, but failed to send notification.", "error": str(e)},
#                             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#                         )

#                 elif action == 'dislike':
#                     print("You disliked the post.")
#                     return Response({"message": "You disliked the post."}, status=status.HTTP_200_OK)

#                 else:
#                     return Response({"message": "Unknown action received."}, status=status.HTTP_200_OK)

#             else:
#                 return Response({"message": f"Failed to like the post"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


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

import json
import urllib.request
import urllib.error
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
def like_on_post(request, post_id, user_id,author_id):
    user_url=""
    like_post_url = f"https://mohammedmoh.pythonanywhere.com/posts/like/{post_id}/{user_id}/"
    send_notification_url = f"https://render-project1-qyk2.onrender.com/notification/send-save-notifications/{author_id}/{user_id}/"
        # Send POST request to like the post
    headers = {'Content-Type': 'application/json'}
    req = urllib.request.Request(like_post_url, method='POST',headers=headers)
    with urllib.request.urlopen(req) as response:
            print(req.data)
            print(response.status)
            print("H"*5)
            print(like_post_url)
            if response.status == 200:
                data = response.read().decode('utf-8')
                result = json.loads(data)
                action = result.get('message')
                if action == 'like':
                    print("You liked the post.")

                    # Send GET request to notification URL
                    notification_data = json.dumps({
                        'content': f"{request.data['name']} like your post",
                        'room_name':f'{author_id}',
                      }).encode('utf-8')
                    try:
                        
                        req2 = urllib.request.Request(send_notification_url, method='POST',headers=headers,data=notification_data)
                        with urllib.request.urlopen(req2) as notify_response:
                            print(notify_response.status)
                            if notify_response.status == 201:
                                return Response(
                                    {"message": "You liked the post and notification sent."},
                                    status=status.HTTP_201_CREATED
                                )
                            else:
                                return Response(
                                    {"message": "You liked the post, but failed to send notification."},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                                )
                    except urllib.error.HTTPError as e:
                        return Response(
                            {"message": "You liked the post, but failed to send notification.", "error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )

                elif action == 'dislike':
                    print("You disliked the post.")
                    return Response({"message": "You disliked the post."}, status=status.HTTP_200_OK)

                else:
                    return Response({"message": "Unknown action received."}, status=status.HTTP_200_OK)

            else:
                return Response({"message": f"Failed to like the post"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['POST'])
def add_comment(request, post_id, user_id,author_id):
    user_url=""
    comment_on_post_url = f"https://mohammedmoh.pythonanywhere.com/posts/addcomment/{post_id}/{user_id}/"
    send_notification_url = f"https://render-project1-qyk2.onrender.com/notification/send-save-notifications/{author_id}/{user_id}/"
        # Send POST request to like the post
    headers = {'Content-Type': 'application/json'}
    comment_data = json.dumps({"text": request.data['text']}).encode('utf-8')
    req = urllib.request.Request(comment_on_post_url, method='POST',headers=headers,data=comment_data)
    with urllib.request.urlopen(req) as response:
            print(req.data)
            print(response.status)
            print("H"*5)
            print(send_notification_url)
            if response.status == 201:
                data = response.read().decode('utf-8')
                result = json.loads(data)
                action = result.get('message')
                if action == 'comment add succesfuly':
                    print("you add comment on this post")

                    # Send GET request to notification URL
                    notification_data = json.dumps({
                        'content': f"{request.data['name']} like your post",
                        'room_name':f'{author_id}',
                      }).encode('utf-8')
                    try:
                        
                        req2 = urllib.request.Request(send_notification_url, method='POST',headers=headers,data=notification_data)
                        with urllib.request.urlopen(req2) as notify_response:
                            print(notify_response.status)
                            if notify_response.status == 201:
                                return Response(
                                    {"message": "You add the comment succesfuly on the post and notification sent."},
                                    status=status.HTTP_201_CREATED
                                )
                            else:
                                return Response(
                                    {"message": "you add comment on the post , but failed to send notification."},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                                )
                    except urllib.error.HTTPError as e:
                        return Response(
                            {"message": "You add commint on the post, but failed to send notification.", "error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )

                else:
                    return Response({"message": "Unknown action received."}, status=status.HTTP_200_OK)

            else:
                return Response({"message": f"Failed to add commint on the post"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(['post'])
# def add_comment(request,post_id,user_id):
#     try:
        
#         profile = Profile.objects.get(user__id=user_id)
#     except Profile.DoesNotExist:
#         return Response({'error': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)
#     try:
       
#         post = Post.objects.get(id=post_id)
#     except Profile.DoesNotExist:
#         return Response({'error': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)
    
#     comment = Comment(writer=profile,post=post,text=request.data['text'])
#     comment.save()
#     return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_comments_on_post(request,post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"error":"post not found."},status=status.HTTP_404_NOT_FOUND) 

    comment = Comment.objects.filter(post=post)   
    serializer = CommentSerializer(comment,many=True)

    return Response(serializer.data)