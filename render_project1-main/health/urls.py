from django.urls import path
from .views import HealthyMealList, delete_meal , search_HealthyMeal,foods,add_diet_plan,get_coach_diet_plans,get_diet_plans,get_meals_in_restaurant,get_restaurants_with_meal,get_trainner_diet_plans,update_dietplan,list_restaurants,list_user_orders,create_restaurant,delete_restaurant,create_order,create_meal, update_meal,update_order_status,add_food,search_meal_time
urlpatterns = [
    path('getdietplane',get_diet_plans , name= "Get Diet Plane"),
    path('healthy-meals/',HealthyMealList,name="health Meals"),
    path('getmealbyname/',search_HealthyMeal,name="GET Meal By Name"),
    path('foods/',foods,name="Get All Food"),
    path('addditeplan/<str:coach_id>/<str:trainer_id>/',add_diet_plan,name="Add Dite Plan"),
    path('coachdietplans/<str:coach_id>/',get_coach_diet_plans,name="Get coach diet_plans"),
    path('gettrainerdietplan/<str:trainer_id>/',get_trainner_diet_plans,name="Get trainner diet_plan"),
    path('updatedietplan/<str:coach_id>/<str:plan_id>/',update_dietplan,name="Update diet_plan"),
    path('listofretaurant/',list_restaurants,name="List of Restaurants"),
    path('ordermeals/<str:user_id>/<str:restaurant_id>/',create_order,name="Order Meals"),
    path('updateorderstatus/<str:order_id>/',update_order_status,name="Update Order Status"),
    path('getuserorders/<str:user_id>/',list_user_orders,name="GET User Order List"),
    path('create_restaurant/',create_restaurant, name='create_restaurant'), #اضافة مطعم
    path('add_food/',add_food, name='add_food'),  # إضافةfood
    path('delete-restaurants/<int:restaurant_id>/',delete_restaurant, name='delete_restaurant'),
    path('create_meal/',create_meal, name='create_meal'),  #اضافة وجبة 
    path('meal_time/',search_meal_time, name='search-diet-plan'), 
    path('restaurants_meal/<str:meal_id>/',get_restaurants_with_meal, name='get restaurant that have that meal'), 
    path('meals_in_restaurant/<str:restaurant_id>/',get_meals_in_restaurant, name='get meal in restaurant'), 
    path('updatemeals/<int:meal_id>/',update_meal, name='update_meal'), 
    path('deletemeal/<int:meal_id>/',delete_meal, name='delete_meal'), 
    
]