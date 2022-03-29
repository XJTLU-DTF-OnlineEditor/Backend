from . import views
from django.urls import path


app_name = 'online_editor'
urlpatterns = [
    path(r'run/interactive/', views.run_interactive, name='execute_interactive'),
    path(r'terminate/', views.terminate, name='terminate'),
    path(r'pic/', views.pic, name='delete_pic'),
]