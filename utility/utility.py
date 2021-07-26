# -*- coding = utf-8 -*-
# @Time : 2021-07-25 13:39
# @Author : Danny
# @File : utility.py
# @Software: PyCharm
from django.contrib.auth.models import User


def exist_username(username):
    if User.objects.filter(username=username).exists():
        return True
    else:
        return False
