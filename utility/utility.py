# -*- coding = utf-8 -*-
# @Time : 2021-07-25 13:39
# @Author : Danny
# @File : utility.py
# @Software: PyCharm
from django.contrib.auth.models import User
from django.http import JsonResponse
import hashlib


def _exist_username(username):
    if User.objects.filter(username=username).exists():
        return True
    else:
        return False


# required_login decorate
def required_login(func):
    def wrapper(request, *args, **kw):
        if not request.user.is_authenticated:
            msg = {
                "status": 2,
                "msg": "account unauthorized"
            }
            return JsonResponse(msg, status=401)
        return func(request, *args, **kw)

    return wrapper


def generateToken(username):
    """
    生成token
    :param username
    :return md5 of the uername
    """
    return hashlib.md5(username.encode('UTF-8')).hexdigest()
