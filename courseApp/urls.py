from django.urls import path

from . import views

app_name = 'courseApp'

urlpatterns = [
    path('courses/<str:topic_title>/', views.Courses, name='Courses'),
    path('coursesDetail/<int:id>/', views.coursesDetail, name='coursesDetail'),
    path('search/', views.search, name='search'),
    path('binlog/', views.binlog),
    path('exercise/<str:topic_title>/<int:id>', views.exercise, name='exercise'),
    path('exercises/<str:topic_title>', views.exercises, name='exercises')
]
