from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    pass

class Followers(models.Model):
    follower = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    followee = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, related_name="user")

class Comments(models.Model):
    comment_text = models.CharField(max_length=256)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="commenter")
    

class Post(models.Model):
    creator = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, related_name="post")
    post_text = models.CharField(max_length=256)
    date = models.DateTimeField(default=timezone.now, verbose_name='date joined')
    likes = models.PositiveIntegerField(default=0)
    comments = models.ForeignKey(Comments, on_delete=models.DO_NOTHING, null=True)

    def serialize(self):
        return {
            "creator": self.creator.username,
            "post_text": self.post_text,
            "date": self.date.strftime("%b %d %Y, %I:%M %p"),
            "likes": self.likes,
            "comments": self.comments
        }

    def __str__(self):
        return f"User: {self.creator.username}, post: {self.post_text}, {self.date}"



