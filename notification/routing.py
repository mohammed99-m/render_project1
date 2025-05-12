# core/routing.py
from django.urls import path
from .consumers import Notification

websocket_urlpatterns = [
    path('ws/notifications/<int:user_id>/', Notification.as_asgi()),  
]