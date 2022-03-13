from django.urls import path
from . import views

app_name = 'courseApp'

urlpatterns = [
    path('topicsByTeacher/', views.TopicsByTeacher, name='TopicsByTeacher'),
    path('courses/<str:topic_title>/', views.Courses, name='Courses'),
    path('courseDetail/<str:topic_title>/<int:id>/', views.coursesDetail, name='coursesDetail'),
    path('search/', views.search, name='search'),
    path('search/<str:keyword>', views.search_topic),
    path('topic/<str:num>', views.top_topic),
    path('newtopic/', views.new_topic),
    path('binlog/', views.binlog),
    path('binlogs/', views.lastModifiedBinlog),
    path('create/', views.create),
    path('edit/', views.edit),
    path('sort/', views.sort),
    path('delete/', views.delete),
    path('upload_topic_img/', views.upload_topic_img),
    path('upload_course_img/<str:topic_title>/', views.upload_course_img),
    path('delete_img/', views.delete_img)
]