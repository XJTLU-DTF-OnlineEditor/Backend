# from django.conf.urls import url
from django.urls import path
from . import views


app_name = 'commitApp'

urlpatterns =[
    path('new/', views.new, name='new'), #最新评论
    path('hot/', views.hot, name='hot'), #热门评论

]