# from django.conf.urls import url
from django.urls import path

from . import views

app_name = 'courseApp'

urlpatterns =[
    # path('basic/$', views.basic, name='basic'), #基础教程
    # path('data/$', views.data, name='data'), #数据分析
    # path('higher/$', views.higher, name='higher'), #进阶教程
    path('Courses/<str:topic_title>/', views.Courses, name = 'Courses'),
    path('coursesDetail/<int:id>/', views.coursesDetail, name = 'coursesDetail'),
    path('search/', views.search, name='search'),
]