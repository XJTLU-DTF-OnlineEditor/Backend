import os
import uuid
from django.db import models
from django.contrib.auth.models import User


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
    # 1 for java, 2 for Python, 3 for C++, 4 for Machine Learning, 5 for Java Web, 6 for Distributed system,
    # 7 for Matlab, 8 for React

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