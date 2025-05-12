from django.urls import path
from .views import NameView
from accounts.views import sign_up ,login , test_token
urlpatterns = [
    path('names/', NameView.as_view(), name='name-list'),

]