# from django.conf.urls import url
from django.urls import path

from . import views
from django.urls import path


app_name = 'online_editor'
urlpatterns = [
    path(r'^$', views.index, name='index'),
    path(r'run$', views.run, name='execute'),
]