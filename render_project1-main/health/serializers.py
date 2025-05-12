from rest_framework import serializers
from accounts.models import Profile
from .models import DietPlan, Meal, MealsSchedule , Restaurant , Food
from accounts.serializers import ProfileSerializer

class FoodSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    calories = serializers.DecimalField(max_digits=100,decimal_places=2)


# class RestaurantSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Restaurant
#         fields = ['restaurant_id', 'name', 'location']

class RestaurantSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    location = serializers.CharField(max_length=255)

class MealSerializer(serializers.Serializer):
    meals_id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=255)
    ingredients = FoodSerializer(many=True)
    price = serializers.FloatField()
    restaurant = RestaurantSerializer(many =True)
   
class MealSerializer2(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ['meals_id', 'name', 'price', 'description', 'restaurant','ingredients']


class DietPlanSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    coach = ProfileSerializer()
    trainer = ProfileSerializer()
    meals = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)


    def get_meals(self, obj):
        schedules = MealsSchedule.objects.filter(dietplan=obj)
        return MealsScheduleSerializer(schedules, many=True).data

    # def create(self, validated_data):
    #     healthymeals_ids = validated_data.pop('healthymeals')
    #     diet_plan = DietPlan.objects.create(**validated_data)
    #     diet_plan.healthymeals.set(healthymeals_ids)
    #     return diet_plan

    # def update(self, instance, validated_data):
    #     healthymeals_data = validated_data.pop('healthymeals', None)
    #     instance.coach = validated_data.get('coach', instance.coach)
    #     instance.trainer = validated_data.get('trainer', instance.trainer)
    #     instance.meal_time = validated_data.get('meal_time', instance.meal_time)
    #     instance.save()

    #     if healthymeals_data is not None:
    #         instance.healthymeals.clear()
    #         for meal_data in healthymeals_data:
    #             healthy_meal = HealthyMeal.objects.create(**meal_data)
    #             instance.healthymeals.add(healthy_meal)

    #     return instance

class MealsScheduleSerializer(serializers.ModelSerializer):
    meal = serializers.PrimaryKeyRelatedField(queryset=Meal.objects.all())
    dietplan = serializers.PrimaryKeyRelatedField(queryset=DietPlan.objects.all())

    class Meta:
        model = MealsSchedule
        fields = ['meal', 'dietplan', 'day' , 'description']
  

from rest_framework import serializers
from .models import Order, OrderMeal, Meal, Restaurant  
from accounts.serializers import ProfileSerializer

from rest_framework import serializers
from .models import Restaurant



class OrderMealSerializer(serializers.Serializer):
    meal = serializers.PrimaryKeyRelatedField(queryset=Meal.objects.all())  
    quantity = serializers.IntegerField()

class OrderSerializer(serializers.Serializer):
    user = ProfileSerializer()
    id = serializers.IntegerField(read_only=True)
    order_meal = OrderMealSerializer(many=True)
    status = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    total_price = serializers.SerializerMethodField()
    serializers.PrimaryKeyRelatedField(read_only=True)

    def get_total_price(self, obj):
        return obj.total_price  

    def create(self, validated_data):
        order_meal_data = validated_data.pop('order_meal', [])
        user = validated_data.pop('user', None)  

        if user is None:
            raise ValueError("User must be provided.")

        order = Order.objects.create(
            status='pending',  
            user=user
        )

        for meal_data in order_meal_data:
            meal_id = meal_data.get('meal')  
            quantity = meal_data.get('quantity', 1)  

            try:
                meal = Meal.objects.get(id=meal_id)
                OrderMeal.objects.create(order=order, meal=meal, quantity=quantity)        
            except Meal.DoesNotExist:
                raise ValueError(f"Meal with id {meal_id} not found.")

        return order

    def update(self, instance, validated_data):
        order_meal_data = validated_data.pop('order_meal', None)
        instance.status = validated_data.get('status', instance.status)
        instance.save()

        if order_meal_data is not None:
            instance.order_meal.all().delete()  
            for meal_data in order_meal_data:
                OrderMeal.objects.create(order=instance, **meal_data)
        instance.save()
        return instance