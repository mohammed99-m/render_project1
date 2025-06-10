from django.urls import path
from .views import send_notification,send_notification2,send_notification3

urlpatterns = [
    path('send-notifications/<str:user_id>/', send_notification, name='send_notification'),
    path('send-notifications-push/<str:user_id>/',send_notification2,name='send_notification2'),
    path('send-notifications-push-updated/<str:user_id>/',send_notification3,name='send_notification3')
]