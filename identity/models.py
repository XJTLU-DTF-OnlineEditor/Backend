import os
import uuid

from django.db import models
from django.contrib.auth.models import User


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

    def icon_url(self):
        if self.user_icon and hasattr(self.user_icon, 'url'):
            return self.user_icon.url
        else:
            return '/media/default/default-user-icon.jpg'

    class Meta:
        verbose_name = 'user_extended'

