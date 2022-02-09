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


# Create your models here.
class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.IntegerField(blank=True)
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


# 用户收藏
class Collect(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True)

    collect_time = models.DateTimeField(auto_now=True)


# 用户点赞
class Like(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True)

    like_time = models.DateTimeField(auto_now=True)
