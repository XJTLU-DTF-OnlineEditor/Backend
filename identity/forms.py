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


