from django.urls import path
from .views import SendMessageView

urlpatterns = [
    path('send/<str:user_id>/', SendMessageView, name='send_message'),
]
