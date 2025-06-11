# core/routing.py
from django.urls import path
from .consumers import Notification

websocket_urlpatterns = [
    path('ws/notifications/<str:room_name>/', Notification.as_asgi()),  
]