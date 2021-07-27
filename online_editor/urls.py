# from django.conf.urls import url
from django.urls import path

from . import views


app_name = 'online_editor'
urlpatterns = [
    path('', views.index, name='index'),
    path('execute', views.execute, name='execute'),
]