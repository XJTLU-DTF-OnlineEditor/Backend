# -*- coding = utf-8 -*-
# @Time : 2021-07-25 13:39
# @Author : Danny
# @File : views.py
# @Software: PyCharm

import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from identity.forms import UploadImageForm
from identity.models import Person
from utility.utility import _exist_username, required_login


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
    tags = request_content.get("tags")

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
                print("user Created")
                person = Person.objects.create(user=user, phone=phone, tags=tags)
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
                    "msg": str(e)
                }
                print(msg)
                return JsonResponse(msg, status=422)
    else:
        msg = {
            "error_code": 422,
            "msg": "Please fill in password twice!"
        }
        return JsonResponse(msg, status=422)


# POST /V1/user/login
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
        return JsonResponse(msg, status=422)

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


# GET /V1/user/logout
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


# GET /v1/user/current-account
@require_http_methods(["GET"])
def current_user(request):
    # cUser = request.user
    # print("UserID: " + str(cUser.id))
    try:
        if request.user.is_authenticated:
            # print("User is authenticated")
            current_user = request.user
            # print(current_user)
            user_content = {
                "username": str(current_user),
                "phone": str(current_user.person.phone),
                "tags": str(current_user.person.tags)
            }
            response = {
                "error_code": 200,
                "msg": "get user success",
                "data": user_content
            }
            return JsonResponse(response, status=200)
        else:
            response = {
                "error_code": 401,
                "msg": "user needs to be authenticated",
            }
            return JsonResponse(response, status=408)
    except:
        response = {
            "error_code": 500,
            "msg": "Internal error"
        }
        return JsonResponse(response, status=500)


# POST account/edit-password/:user-id
@require_http_methods(["POST"])
def change_user_password(request):
    try:
        if request.user.is_authenticated:
            current_user = request.user
            request_content = json.loads(request.body)
            try:
                new_password1 = request_content.get("new_password1")
                new_password2 = request_content.get("new_password2")
                if new_password1 == new_password2:
                    current_user.set_password(request_content.get("new_password1"))
                    # print(current_user.password)
                    current_user.save()
                    return JsonResponse({
                        "error_code": 200,
                        "msg": "password change successfully"
                    }, status=200)
                else:
                    return JsonResponse({
                        "error_code": 402,
                        "msg": "two passwords are not the same."
                    }, status=402)
            except Exception as e:
                msg = {
                    "error_code": 408,
                    "msg": str(e)
                }
                return JsonResponse(msg, status=422)
        else:
            msg = {
                "status": 401,
                "msg": "account unauthorized"
            }
            return JsonResponse(msg, status=401)
    except Exception as e:
        msg = {
            "status": 500,
            "msg": str(e)
        }
        return JsonResponse(msg, status=500)


# POST account/icon/
@require_http_methods(["POST"])
@required_login
def edit_usericon(request):
    form = UploadImageForm(request.POST, request.FILES)
    if form.is_valid():
        request.user.person.user_icon = request.FILES['image']
        request.user.person.save()

        msg = {
            "error_code": 200,
            "msg": "success update icon"
        }
        return JsonResponse(msg, status=200)

    else:
        msg = {
            "error_code": 402,
            "msg": "invalid form"
        }
        return JsonResponse(msg, status=422)


"""
 POST /V1/user/edit-info
 
 -> {
    "tags": The value to be modified,
    "phone": The value to be modified,
 }
 
 <- {
    "error_code": 200,
    "msg": messages about the request state,
    "tags": 1 if tags has been modified,
    "phone": 1if phone has been modified,
 }
"""


@require_http_methods(["GET"])
def edit_userInfo(request):
    if request.user.is_authenticated:
        current_user = request.user
        request_content = json.loads(request.body)
        msg = {
            "error_code": 402,
            "msg": "Server doesn't understand the syntax",
            "tags": 0,
            "phone": 0,
        }
        response_msg = "updated "
        modified = False
        if "tags" in request_content.keys():
            current_user.person.tags = request_content.get("tags")
            msg["tags"] = 1
            msg["error_code"] = 200
            response_msg += "tags "
            modified = True
        if "phone" in request_content.keys():
            current_user.person.phone = request_content.get("phone")
            msg["phone"] = 1
            msg["error_code"] = 200
            response_msg += "and phone "
            modified = True
        # if ... other entities have been changed
        current_user.person.save()
        # print(current_user.person.phone)
        # print(current_user.person.tags)
        if modified:
            msg["msg"] = response_msg
        return JsonResponse(msg, status=200)
    else:
        msg = {
            "error_code": 401,
            "msg": "account needs to be authenticated"
        }
        return JsonResponse(msg, status=401)
