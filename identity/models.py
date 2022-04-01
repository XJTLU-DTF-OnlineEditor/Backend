import os
import uuid

from django.db import models
from django.contrib.auth.models import User
from courseApp.models import Topic


def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4().hex[:10], ext)
    # return the whole path to the file
    return os.path.join('user_imgs', str(instance.user.id), "user_icon", filename)


# Student model
class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=50, verbose_name="Token Auth", null=True, blank=True)
    username = models.CharField(blank=True, null=True, max_length=20)
    user_icon = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    tags = models.CharField(blank=True, null=True,
                            max_length=20)  # tags chosen by users, each number has the designated skill

    def icon_url(self):
        if self.user_icon and hasattr(self.user_icon, 'url'):
            return self.user_icon.url
        else:
            return '/media/default/default-user-icon.jpg'

    class Meta:
        verbose_name = 'user_extended'

# temp email verification
class VerificationEmail(models.Model):
    email = models.EmailField()
    verification_code = models.CharField(max_length=10)


# Teacher model
class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=50, verbose_name="Token Auth", null=True, blank=True)
    admin_name = models.CharField(blank=True, null=True, max_length=20)


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


# 老师发布的课程
class teacherCourses(models.Model):
    teacher = models.ForeignKey(Admin, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
