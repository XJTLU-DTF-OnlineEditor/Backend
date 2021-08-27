
from django.urls import path

from . import views

app_name = 'courseApp'

urlpatterns =[
    path('Courses/<str:topic_title>/', views.Courses, name = 'Courses'),
    path('coursesDetail/<int:id>/', views.coursesDetail, name = 'coursesDetail'),
    path('search/', views.search, name='search'),
]