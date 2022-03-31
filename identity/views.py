# -*- coding = utf-8 -*-
# @Time : 2021-07-25 13:39
# @Author : Danny
# @File : views.py
# @Software: PyCharm

import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse

from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from identity.forms import UploadImageForm, UserRegisterForm
from identity.models import Person, Admin, teacherCourses
from utility.utility import _exist_username, required_login, generateToken
from django.core.mail import send_mail

# Create your views here.


"""
Post /V1/user/register
-> {
    "type": teacher or student
    "email": string@xjtlu.student.edu.cn
    "username": String
    "password: String (3 < length < 15)
}

"""


@require_http_methods(["POST"])
def user_register(request):
    request_content = json.loads(request.body)
    print(request_content)
    email = request_content.get("email")
    if email:
        if _exist_username(email):
            msg = {
                "status": 422,
                "msg": "email address already in use, please directly log in."
            }
            return JsonResponse(msg, status=422)
    else:
        msg = {
            "status": 422,
            "msg": "Received empty email address."
        }
        return JsonResponse(msg, status=422)

    type = request_content.get("type")
    password = request_content.get("password")
    username = request_content.get("username")

    if password is not None:
        if type == "student":
            try:
                user = User.objects.create_user(username=email, password=password)
                person = Person.objects.create(user=user, username=username)
                user.save()
                person.save()
                user = authenticate(request, username=email, password=password)
                login(request, user)

                msg = {
                    "status": 200,
                    "msg": "Student register and login success"
                }
                return JsonResponse(msg, status=200)
            except Exception as e:
                msg = {
                    "status": 201,
                    "msg": str(e)
                }
                return JsonResponse(msg, status=422)
        elif type == "teacher":
            try:
                user = User.objects.create_user(username=email, password=password)
                admin = Admin.objects.create(user=user, admin_name=username)
                user.save()
                admin.save()
                user = authenticate(request, username=email, password=password)
                login(request, user)

                msg = {
                    "status": 200,
                    "msg": "teacher register and login success"
                }
                return JsonResponse(msg, status=200)
            except Exception as e:
                msg = {
                    "status": 201,
                    "msg": str(e)
                }
                return JsonResponse(msg, status=422)
    else:
        msg = {
            "status": 422,
            "msg": "empty password"
        }
        return JsonResponse(msg, status=422)


"""
<- POST
{
    "email": string
    "password": string
    “type”: string
}
->
{
    "status": "ok",
    "error_code": 200,
    "type": type,
    "msg": "login successfully",
    "token": token,
    "currentAuthority": currentAuthority
}
"""


# POST /V1/user/login
@require_http_methods(["POST"])
def user_login(request):
    request_content = json.loads(request.body)
    email = request_content.get("email")
    password = request_content.get("password")
    userType = request_content.get("userType")
    # print(password)
    # print(email)
    # print(userType)

    if not _exist_username(email):
        msg = {
            "status": "error",
            'error_code': 422,
            "type": "login",
            'msg': 'User account not found, please register first',
            "currentAuthority": "guest"
        }
        return JsonResponse(msg)

    user = authenticate(request, username=email, password=password)
    currentAuthority = "user"
    if user is not None:
        token = generateToken(email)
        if userType == "student":
            student = Person.objects.get(user__username=email)
            student.token = token
            student.save()
        if userType == "teacher":
            teacher = Admin.objects.get(user__username=email)
            teacher.token = token
            teacher.save()
            currentAuthority = "admin"
        login(request, user)

    else:
        msg = {
            "status": "error",
            "error_code": 422,
            "type": "login",
            "msg": "invalid login, please check email or password!",
            "currentAuthority": "guest"
        }
        return JsonResponse(msg)
    msg = {
        "status": "ok",
        "error_code": 200,
        "userType": userType,
        "msg": "login successfully",
        "token": token,
        "currentAuthority": currentAuthority
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
    cUser = request.user
    token = request.META.get("HTTP_TOKEN")
    currentAuthority = request.META.get("HTTP_CURRENTAUTHORITY")
    # print(token)
    # print(currentAuthority)
    # print("UserID: " + str(cUser.id))
    if len(token) != 0 & request.user.is_authenticated:
        try:
            current_user = request.user
            if currentAuthority == "user":
                student = Person.objects.get(token=token)
                user_content = {
                    "currentAuthority": "user",
                    "username": str(student.username),
                    "email": str(current_user.username),
                    "tags": str(current_user.person.tags),
                    "avator": "http://127.0.0.1:8000/media/" + str(student.user_icon)
                }
                response = {
                    "status": "ok",
                    "error_code": 200,
                    "msg": "get user success",
                    "data": user_content
                }
                return JsonResponse(response, status=200)
            elif currentAuthority == "admin":
                teacher = Admin.objects.get(token=token)
                teacherTopic_list = teacherCourses.objects.filter(teacher__token=token)
                # Add teacher's topics to a list
                topic_collection = []
                for item in teacherTopic_list:
                    topic_dict = {
                        "topic_id": item.topic.topic_id,
                        "topic_title": item.topic.topic_title,
                    }
                    topic_collection.append(topic_dict)
                user_content = {
                    "currentAuthority": "admin",
                    "username": str(teacher.admin_name),
                    "email": str(teacher.user.username),
                    "topics": topic_collection
                }
                response = {
                    "status": "ok",
                    "error_code": 200,
                    "msg": "get user success",
                    "data": user_content
                }
                return JsonResponse(response, status=200)
        except Exception as e:
            response = {
                "error_code": 500,
                "msg": str(e)
            }
            return JsonResponse(response, status=500)
    else:
        response = {
            "error_code": 403,
            "msg": "user needs to be authorized"
        }
        return JsonResponse(response, status=403)



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


"""
POST /V1/user/verify_email
->{
    "email": String
    "email_id": int  # Random integer to clarify the email  
}

<-{
    "error_code": 200
    "msg": success
}
"""


@require_http_methods(["POST"])
@required_login
def send_verify_email(request):
    request_content = json.loads(request.body)
    email = request_content.get("email")
    email_id = request_content.get("email_id")
