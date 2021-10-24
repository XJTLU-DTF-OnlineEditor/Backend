from django.contrib import admin
from .models import MyCourse, Topic

admin.site.site_header = "Python 在线学习后台管理网站"
admin.site.site_title = "Python 在线学习后台管理网站"

"""
Ueditor 来插入课程文件
"""


class MyCourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'related_topic', 'update_date', 'views')
    style_fields = {'description': 'ueditor'}
    search_fields = ('title', 'realated_topic')

    def related_topics(self):
        return MyCourse.related_topic.topic_title


admin.site.register(MyCourse, MyCourseAdmin)

"""
topic 的models还未规范需要与kiki确定才能部署
"""


class TopicAdmin(admin.ModelAdmin):
    list_display = ('topic_title',)
    style_fields = {'topic_content': 'ueditor'}


admin.site.register(Topic, TopicAdmin)
