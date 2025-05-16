from django.urls import path
from .views import SendMessageView

urlpatterns = [
    path('send/<str:sender_id>/<str:reciver_id>/', SendMessageView, name='send_message'),
]
