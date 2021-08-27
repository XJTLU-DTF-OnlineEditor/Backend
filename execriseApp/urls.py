# from django.conf.urls import url
from django.urls import path

from . import views

app_name = 'execriseApp'

urlpatterns =[
    path('basic/', views.basic, name='basic'), #Python3 教程
    path('data/', views.data, name='data'), #Python3 待定
    path('higher/', views.higher, name='higher'), #进阶教程

]