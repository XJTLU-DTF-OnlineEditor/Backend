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

    password1 = request_content.get("password1")
    password2 = request_content.get("password2")
    phone = request_content.get("phone")

    if password1 is not None and password2 is not None:
        if not password1 == password2:
            msg = {
                "error": 422,
                "msg": "second password is not the same as the first one."
            }
            return JsonResponse(msg, status=422)
        if phone is None:
            msg = {
                "error": 422,
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
            "msg": "Please fill in password twice!"
        }
        return JsonResponse(msg, status=422)
