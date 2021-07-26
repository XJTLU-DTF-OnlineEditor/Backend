# -*- coding = utf-8 -*-
# @Time : 2021-07-25 13:39
# @Author : Danny
# @File : views.py
# @Software: PyCharm

import json

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse

from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from identity.models import Person
from utility.utility import *


# Create your views here.


# POST /register
@require_http_methods(["POST"])
def user_register(request):
    request_content = json.loads(request.body)
    username = request_content.get("username")

    if username:
        if exist_username(username):
            msg = {
                "error": 422,
                "msg": "username already in use"
            }
            return JsonResponse(msg, status=422)
    else:
        msg = {
            "error": 422,
            "msg": "received empty username"
        }
        return JsonResponse(msg, status=422)

    password = request_content.get("password")
    phone = request_content.get("phone")

    if password is not None and phone is not None:
        try:
            user = User.objects.create_user(username=username, password=password)
            person = Person.objects.create(user=user, phone=phone)
            user.save()
            person.save()
            user = authenticate(request, username=username, password=password)
            login(request, user)

            print(request.user.is_authenticated)

            msg = {
                "error": 200,
                "msg": "register success"
            }
            return JsonResponse(msg, status=200)

        except Exception as e:
            msg = {
                "error": 422,
                "msg": e
            }
            return JsonResponse(msg, status=422)

    else:
        msg = {
            "error": 422,
            "msg": "empty password or phone"
        }
        return JsonResponse(msg, status=422)