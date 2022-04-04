from django.db import models
from courseApp.models import Topic
from identity.models import Person


# 学生收藏
class Collect(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    collect_time = models.DateTimeField(auto_now=True)


# 学生点赞
class Like(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    like_time = models.DateTimeField(auto_now=True)


# 学生浏览记录
class history(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)