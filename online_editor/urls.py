# from django.conf.urls import url
from django.urls import path

from . import views
from django.urls import path


app_name = 'online_editor'
urlpatterns = [
    path(r'run/', views.run, name='execute'),
]