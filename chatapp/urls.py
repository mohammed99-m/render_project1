from django.urls import path
from .views import SendMessageView

urlpatterns = [
    path('send/<int:user_id>/', SendMessageView, name='send_message'),
]
