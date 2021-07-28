from django.contrib import admin
from . models import MyCourse

admin.site.site_header = "Python 在线学习后台管理网站"
admin.site.site_title = "Python 在线学习后台管理网站"


"""
Ueditor 来插入课程文件
"""
class MyCourseAdmin(admin.ModelAdmin):
    style_fields = {'description':'ueditor'}

admin.site.register(MyCourse,MyCourseAdmin)
