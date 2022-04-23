# -*- coding = utf-8 -*-
# @Time : 2021-07-25 13:39
# @Author : Danny
# @File : views.py
# @Software: PyCharm

import json
import random
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from Django_editor_backend import settings
from courseApp.models import MyCourse, Topic
from identity.forms import UploadImageForm
from identity.models import Person, Admin, VerificationEmail
from identity.student_action_models import History, Collect
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
    # print(request_content)
    email = request_content.get("email")
    try:
        verifiedEmail = VerificationEmail.objects.get(email=email)
        verification_code = verifiedEmail.verification_code
    except Exception as e:
        msg = {
            "status": "error",
            "error_code": 420,
            "msg": str(e) + " Obtain verification code first"
        }
        return JsonResponse(msg)
    if _exist_username(email):  # check If the email has already existed
        msg = {
            "status": "error",
            "error_code": 421,
            "msg": "email address already in use, please directly log in."
        }
        verifiedEmail.delete()
        return JsonResponse(msg)
    verification_code_pre = request_content.get("captcha")

    if verification_code == verification_code_pre:  # Check captcha if is the same as previous one
        userType = request_content.get("userType")
        password = request_content.get("password")
        username = request_content.get("username")
        if password is not None:
            token = generateToken(email)
            currentAuthority = "user"
            if userType == "student":
                try:
                    user = User.objects.create_user(username=email, password=password)
                    person = Person.objects.create(user=user, username=username, token=token)
                    user.save()
                    person.save()
                    user = authenticate(request, username=email, password=password)
                    login(request, user)
                    verifiedEmail.delete()  # delete the email verification that has already been verified
                except Exception as e:
                    msg = {
                        "status": 201,
                        "msg": str(e)
                    }
                    return JsonResponse(msg, status=422)
            elif userType == "teacher":
                currentAuthority = "admin"
                try:
                    user = User.objects.create_user(username=email, password=password)
                    admin = Admin.objects.create(user=user, admin_name=username, token=token)
                    user.save()
                    admin.save()
                    user = authenticate(request, username=email, password=password)
                    login(request, user)
                    verifiedEmail.delete()
                except Exception as e:
                    msg = {
                        "status": 201,
                        "msg": str(e)
                    }
                    return JsonResponse(msg, status=422)
            msg = {
                "status": "ok",
                "error_code": 200,
                "userType": userType,
                "msg": "Register and login successfully",
                "token": token,
                "currentAuthority": currentAuthority
            }
            return JsonResponse(msg, status=200)
        else:
            msg = {
                "status": "error",
                "error_code": 422,
                "msg": "Password is empty!"
            }
            return JsonResponse(msg, status=422)
    else:
        msg = {
            "status": "error",
            "error_code": 422,
            "msg": "Verification code is not correct!"
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


'''
GET
<- header: {
    "token": string
    "currentAuthority": string
}

->
currentAuthority == "user":
    {
        "status": "ok",
        "error_code": 200,
        "msg": "get user success",
        "data": {
            "currentAuthority": "user",
            "userid": student.user_id,
            "username": str(student.username),
            "email": str(current_user.username),
            "tags": str(current_user.person.tags),
            "avator": "/media/" + str(student.user_icon),
            "history": {
                "topic": topic,
                "topic_img": str("http://120.26.46.74:4000/media/") + str(topic_pic),
                "progress": progress,
                "last_practice_time": last_practice_time,
                "finished_courses": [],
                "unfinished_courses": [],
                "progress_course": {
                    "title": progress_course,
                    "id": progress_course_id
                }
            }
        } 
    }
currentAuthority == "admin":
{
    "status": "ok",
    "error_code": 200,
    "msg": "get user success",
     "data": {
        "currentAuthority": "user",
        "userid": student.user_id,
        "username": str(student.username),
        "email": str(current_user.username),
        "tags": str(current_user.person.tags),
        "avator": "/media/" + str(student.user_icon),
            "history": {
                "topic": topic,
                "topic_img": str("http://120.26.46.74:4000/media/") + str(topic_pic),
                "progress": progress,
                "last_practice_time": last_practice_time,
                "finished_courses": [],
                "unfinished_courses": [],
                "progress_course": {
                    "title": progress_course,
                    "id": progress_course_id
                }
            }
        } 
    }

'''


# GET /v1/user/current-account
@require_http_methods(["GET"])
def current_user(request):
    cUser = request.user
    token = request.META.get("HTTP_TOKEN")
    # print("token: " + token)
    # print(cUser)
    if token == "null":
        print("guest")
        msg = {
            "status": "ok",
            "error_code": 403,
            "msg": "user not login",
            "data": {
                "currentAuthority": "guest"
            }
        }
        return JsonResponse(msg)

    currentAuthority = request.META.get("HTTP_CURRENTAUTHORITY")
    # print(token)
    # print(currentAuthority)
    # print("UserID: " + str(cUser.id))
    if (token != "null") & (request.user.is_authenticated):
        try:
            current_user = request.user
            if currentAuthority == "user":
                student = Person.objects.get(token=token)
                history_objs = History.objects.filter(person__token=token)
                history_list = []
                for history_obj in history_objs:  # add history into one list
                    finished_course_list = []
                    # find the last course which is the one user is working on
                    history_num = history_obj.course.count()
                    for course in history_obj.course.all():  # find users finished courses
                        finished_course_list.append(course.title)
                    progress_course = finished_course_list[history_num - 1]
                    progress_course_id = MyCourse.objects.get(
                        title=progress_course).subtopic_id  # find the corresponding id of progress course
                    topic = history_obj.topic.topic_title
                    topic_pic = history_obj.topic.topic_img
                    # Calculate progress
                    all_courses_obj = MyCourse.objects.filter(related_topic__topic_title=topic)
                    courses_num = all_courses_obj.count()
                    all_courses_list = []
                    for courses in all_courses_obj:  # find all the related courses
                        all_courses_list.append(courses.title)
                    unfinished_courses_list = []
                    for course in all_courses_list:  # find all the unfinished courses
                        if course not in finished_course_list:
                            unfinished_courses_list.append(course)
                    finished_course_list.pop()  # Pop the last in progress one
                    progress = "%s/%s" % (len(finished_course_list), courses_num)
                    last_practice_time = history_obj.last_practice_time
                    history_list.append({
                        "topic": topic,
                        "topic_img": str("http://120.26.46.74:4000/media/") + str(topic_pic),
                        "progress": progress,
                        "last_practice_time": last_practice_time,
                        "finished_courses": finished_course_list,
                        "unfinished_courses": unfinished_courses_list,
                        "progress_course": {
                            "title": progress_course,
                            "id": progress_course_id
                        }
                    })
                collection_objs = Collect.objects.filter(person__token=token)
                collection_list = []
                for collection in collection_objs:
                    topic_obj = collection.topic
                    collection_dict = {
                        "topic_title": topic_obj.topic_title,
                        "topic_content": topic_obj.topic_description,
                        "topic_img": str("/media/") + str(topic_obj.topic_img),
                        "collection_time": collection.collect_time
                    }
                    collection_list.append(collection_dict)
                user_content = {
                    "currentAuthority": "user",
                    "userid": student.user_id,
                    "username": str(student.username),
                    "email": str(current_user.username),
                    "tags": str(current_user.person.tags),
                    "avator": "/media/" + str(student.user_icon),
                    "history": history_list,
                    "collections": collection_list
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
                user_content = {
                    "userid": teacher.user_id,
                    "currentAuthority": "admin",
                    "username": str(teacher.admin_name),
                    "email": str(teacher.user.username),
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
            return JsonResponse(response)
    else:
        msg = {
            "status": "ok",
            "error_code": 403,
            "msg": "user not login",
            "data": {
                "currentAuthority": "guest"
            }
        }
        return JsonResponse(msg)


"""
send verify email
<- POST
{
    "email": string
}
->{
    "status": "ok",
    "error_code": 200,
    "msg": verification code sent successfully
    "data": {
        "code": String
    }
}
"""


@require_http_methods(["POST"])
def send_verify_email(request):
    email_list = []
    email = json.loads(request.body).get("email")
    email_list.append(email)
    # print(email)
    verification = str(random.randint(100000, 999999))
    # print(verification)
    email_from = settings.EMAIL_FROM
    message = "Your verification code is: " + verification + ", do not tell others your code!"
    send_status = send_mail('Verification code', message, email_from, email_list)
    # print(send_status)
    if send_status == 1:
        verificationObj = VerificationEmail.objects.create(email=email, verification_code=verification)
        verificationObj.save()
        msg = {
            "status": "ok",
            "error_code": 200,
            "msg": "verification code sent successfully",
            "data": {
                "code": verification
            }
        }
    else:
        msg = {
            "status": "error",
            "error_code": 201,
            "msg": "verification code did not send",
        }
    return JsonResponse(msg, status=200)


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


@require_http_methods(["GET"])
def user_course_progress(request):
    token = request.META.get("HTTP_TOKEN")
    cuser = request.user
    print(cuser)
    if token == "null":
        print("guest")
        msg = {
            "status": "ok",
            "error_code": 403,
            "msg": "user not login",
            "data": {
                "currentAuthority": "guest"
            }
        }
        return JsonResponse(msg)
    current_authority = request.META.get("HTTP_CURRENTAUTHORITY")
    # if (token != "null") & request.user.is_authenticated:
    #     try:
    #         current_user = request.user

    msg = {

    }
    return JsonResponse(msg)
