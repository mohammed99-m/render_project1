from django.contrib import admin
from .models import DietPlan
from .models import Meal, Order, OrderMeal, Restaurant , Food
admin.site.register(DietPlan)
admin.site.register(Restaurant)
admin.site.register(Meal)
admin.site.register(Order)
admin.site.register(OrderMeal)
admin.site.register(Food)