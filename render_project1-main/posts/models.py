from django.db import models
from accounts.models import Profile
# Create your models here.


class Post(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    like = models.ManyToManyField(Profile)
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    def __str__(self):
        return f"Post by {self.author.user.username} - {self.content[:20]}"
    

class Comment(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name="comment")
    writer = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name="writer")
    text = models.TextField()
    time = models.DateTimeField(auto_now_add=True)




    

