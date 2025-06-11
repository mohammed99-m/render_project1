from django.db import models
from django.db import models
from accounts.models import Profile


class Restaurant(models.Model):
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=255)
  location = models.CharField(max_length=255)

  def __str__(self):
     return self.name

class Food(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    calories = models.DecimalField(max_digits=100,decimal_places=2)


class Meal(models.Model):
    meals_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.FloatField()
    description = models.TextField()
    #photo = models.URLField()
    ingredients = models.ManyToManyField(Food, related_name='ingredients_food')
    restaurant = models.ManyToManyField(Restaurant, related_name='restaurant')
    
    def str(self):
      return self.name#ا
  
class Order(models.Model):
  user = models.ForeignKey(Profile, on_delete=models.CASCADE)
  meals = models.ManyToManyField(Meal, through='OrderMeal')
  status = models.CharField(max_length=10, default='pending')
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
      return f"Order {self.id} - {self.status}"
  @property
  def total_price(self):
      total = sum(order_meal.quantity * order_meal.meal.price for order_meal in self.order_meal.all())
      return total

class OrderMeal(models.Model):
  order = models.ForeignKey(Order, related_name='order_meal', on_delete=models.CASCADE)
  meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
  quantity = models.PositiveIntegerField(default=1)


class DietPlan(models.Model):
    id = models.AutoField(primary_key=True)
    coach = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name="health_Program_maker")
    trainer = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name="health_Program_assigned")
    meals = models.ManyToManyField(Meal, related_name='diet_plans')
    created_at = models.DateTimeField(auto_now_add=True)
       

class MealsSchedule(models.Model):
   meal=models.ForeignKey(Meal, on_delete=models.CASCADE)  
   dietplan = models.ForeignKey(DietPlan,on_delete=models.CASCADE)
   day = models.CharField(max_length=10)
   description = models.TextField(max_length=500,blank=True, null=True)



   def __str__(self):
        return f"{self.meal.name} on {self.day} for {self.dietplane.description}"