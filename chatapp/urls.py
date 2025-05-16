from django.urls import path
from .views import SendMessageView,SendMessageView2

urlpatterns = [
    path('send/<str:sender_id>/<str:reciver_id>/', SendMessageView, name='send_message'),
    path('send_message/<str:user_id>/', SendMessageView2, name='send_message2'),
]
