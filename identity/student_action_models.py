from django.db import models
from courseApp.models import Topic, MyCourse
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


# 学生点击课程后浏览记录，随进度更新
class History(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    course = models.ManyToManyField(to=MyCourse, verbose_name="course_progress")
    last_practice_time = models.DateTimeField(verbose_name="上次练习时间", name="last_practice_time")