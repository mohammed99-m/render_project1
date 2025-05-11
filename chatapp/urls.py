from django.urls import path
from .views import SendMessageView

urlpatterns = [
    path('send/', SendMessageView, name='send_message'),
]
