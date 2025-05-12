from django.urls import path
from .views import send_notification

urlpatterns = [
    path('send-notifications/<str:user_id>/', send_notification, name='send_notification'),
]