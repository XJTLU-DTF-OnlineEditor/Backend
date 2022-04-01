# -*- coding = utf-8 -*-
# @Time : 2021-07-26 17:35
# @Author : Danny
# @File : urls.py
# @Software: PyCharm

from django.urls import path
from identity import views
from django.conf.urls import include


app_name = 'identity'
urlpatterns = [
    path('register/', views.user_register),
    path('login/', views.user_login),
    path('logout/', views.user_logout),
    path('currentuser/', views.current_user),
    path('change_password/', views.change_user_password),
    path('icon/', views.edit_usericon),
    path('edit_userInfo/', views.edit_userInfo),
    path('send_verification_email/', views.send_verify_email)
]