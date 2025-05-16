from django.urls import path
from .views import add_comment , get_all_posts , get_comments_on_post , like_on_post , get_someone_posts

urlpatterns = [
  ##path('addpost/<author_id>/',add_post,name="Add Post"),
  path('addcomment/<str:post_id>/<str:user_id>/<str:author_id>/',add_comment,name="Add Comment"),
  path('like/<str:post_id>/<user_id>/<str:author_id>',like_on_post,name="Like On Post"),
  path('getallposts/',get_all_posts,name="Get All Post"),
  path('getsomeoneposts/<str:user_id>/',get_someone_posts,name='Get Someone Post'),
  path('getcommentsonpost/<str:post_id>/',get_comments_on_post,name="Get Comments On Post")
]


