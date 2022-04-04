# -*- coding = utf-8 -*-
# @Time : 2021-09-08 16:57
# @Author : Danny
# @File : forms.py
# @Software: PyCharm
from django import forms
from .models import Person


class UploadImageForm(forms.Form):
    name = forms.CharField(max_length=256)
    image = forms.ImageField()


class UserRegisterForm(forms.Form):
    type = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, min_length=6, max_length=15, error_messages={
        "required": "Password is required",
        "min_length": "Password length is at least three",
        "max_length": "Password length is at most 15"
    })
    username = forms.CharField(required=False, max_length=20, error_messages={
        "max_length": "username cannot be more than 20 characters"
    })
    tag = forms.CharField(required=False)
    user_icon = forms.ImageField(required=False)