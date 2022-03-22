# from django.conf.urls import url
from django.urls import path

from . import views
from django.urls import path


app_name = 'online_editor'
urlpatterns = [
    path(r'run/split/', views.run_split, name='execute_split'),
    path(r'run/interactive/', views.run_interactive, name='execute_interactive'),
    path(r'terminate/', views.terminate, name='terminate'),
]