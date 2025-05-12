# core/routing.py
from django.urls import path
from .consumers import Notification
from . import consumers

websocket_urlpatterns = [
    path('ws/notifications/<int:user_id>/', consumers.Notification.as_asgi()),  
]