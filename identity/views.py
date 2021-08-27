# -*- coding = utf-8 -*-
# @Time : 2021-07-25 13:39
# @Author : Danny
# @File : views.py
# @Software: PyCharm

import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse

from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from identity.models import Person
from utility.utility import _exist_username

# from aliyunsdkcore.client import AcsClient
# from aliyunsdkcore.request import CommonRequest


# Create your views here.


# POST /register
@require_http_methods(["POST"])
def user_register(request):
    request_content = json.loads(request.body)
    username = request_content.get("username")

    if username:
        if _exist_username(username):
            msg = {
                "error_code": 422,
                "msg": "username already in use"
            }
            return JsonResponse(msg, status=422)
    else:
        msg = {
            "error_code": 422,
            "msg": "received empty username"
        }
        return JsonResponse(msg, status=422)

    password1 = request_content.get("password1")
    password2 = request_content.get("password2")
    phone = request_content.get("phone")

    if password1 is not None and password2 is not None:
        if not password1 == password2:
            msg = {
                "error_code": 422,
                "msg": "second password is not the same as the first one."
            }
            return JsonResponse(msg, status=422)
        if phone is None:
            msg = {
                "error_code": 422,
                "msg": "empty phone number."
            }
            return JsonResponse(msg, status=422)
        else:
            try:

                user = User.objects.create_user(username=username, password=password1)
                person = Person.objects.create(user=user, phone=phone)
                user.save()
                person.save()
                user = authenticate(request, username=username, password=password1)
                login(request, user)

                # print(request.user.is_authenticated)

                msg = {
                    "error_code": 200,
                    "msg": "register success"
                }
                return JsonResponse(msg, status=200)

            except Exception as e:
                msg = {
                    "error_code": 422,
                    "msg": e
                }
                return JsonResponse(msg, status=422)
    else:
        msg = {
            "error_code": 422,
            "msg": "Please fill in password twice!"
        }
        return JsonResponse(msg, status=422)


# POST /login
@require_http_methods(["POST"])
def user_login(request):
    request_content = json.loads(request.body)
    username = request_content.get("user_name")
    password = request_content.get("password")

    if not _exist_username(username):
        msg = {
            'error_code': 422,
            'msg': 'User account not found, please register first'
        }
        return JsonResponse(msg, status=401)

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
    else:
        msg = {
            "error_code": 422,
            "msg": "invalid login"}
        return JsonResponse(msg, status=422)
    msg = {
        "error_code": 200,
        "msg": "login successfully"
    }
    return JsonResponse(msg, status=200)


# GET /logout
@require_http_methods(["GET"])
def user_logout(request):
    try:
        logout(request)
    except Exception as e:
        msg = {
            "error_code": 422,
            "msg": "logout failed" + str(e),
        }
        return JsonResponse(msg, status=422)
    msg = {
        "error_code": 200,
        "msg": "logout successfully"
        }
    return JsonResponse(msg, status=200)