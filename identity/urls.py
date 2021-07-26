# -*- coding = utf-8 -*-
# @Time : 2021-07-26 17:35
# @Author : Danny
# @File : urls.py
# @Software: PyCharm

from django.urls import path
from identity import views


app_name = 'identity'
urlpatterns = [
    path('register/', views.user_register)
]