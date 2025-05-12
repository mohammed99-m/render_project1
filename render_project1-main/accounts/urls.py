from django.urls import path
from . import views
urlpatterns = [
    path('register/',views.sign_up, name='Register'),
    path('login/',views.login,name='Login'),
    path('delete/',views.delete_account,name="Delete"),
    path('getInfo/',views.test_token,name="GET Informations"),
    path('update_profile/',views.update_profile_field,name="Updet Information"),
    path('users/',views.get_users,name="GET Users"),
    path('coaches/',views.get_coaches, name="GET Coaches"),
    path('user/<str:user_id>/',views.get_specific_user,name="Get Uesr"),
    path('trainers/<str:coach_id>/',views.get_trainers,name="Trainers With Specific Coach"),
    path('sendjoinrequest/<str:user_id>/<str:coach_id>/',views.send_join_request,name="Send Join Request"),
    path('responsetojoinrequest/<str:coach_id>/<str:request_id>/',views.respond_to_join_request,name="Response To Join Request"),
    path('getjoinrequests/<str:coach_id>/',views.get_join_requests,name="Get All Join Requestes"),
    path('getgoals/',views.return_goals,name="Get Goals"),
    path('getexperincelevel/',views.return_experince_level,name="Experince Level"),
    path('getrequeststatus/<str:trainer_id>/',views.get_request_status,name="Request Status"),
    path('gettrainerinfo/<str:trainer_id>/<str:coach_id>/',views.get_trainer_info,name="Get Trainer Info")
]