from django.urls import path

from . import views

app_name = 'courseApp'

urlpatterns = [
    path('topicsByTeacher/', views.TopicsByTeacher, name='TopicsByTeacher'),
    path('courses/<str:topic_title>/', views.Courses, name='Courses'),
    path('courseDetail/<str:topic_title>/<int:id>/', views.coursesDetail, name='coursesDetail'),
    path('search/<str:keyword>', views.search_topic, name='search'),
    path('search/', views.search),
    path('topic/', views.top_topic),
    path('binlog/', views.binlog),
    path('binlogs/', views.lastModifiedBinlog),
    # path('exercises/<str:topic_title>', views.exercises, name='exercises'),
    path('create/', views.create),
    path('delete/', views.delete),
    path('edit/', views.edit)
]
