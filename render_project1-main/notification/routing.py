# core/routing.py
from django.urls import path
from .consumers import Notification
from . import consumers

websocket_urlpatterns = [
    path('ws/notifications/<str:room_name>/', consumers.Notification.as_asgi()),  
]