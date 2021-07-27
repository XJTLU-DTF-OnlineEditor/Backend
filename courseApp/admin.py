from django.contrib import admin
from . models import MyCourse

class MyCourseAdmin(admin.ModelAdmin):
    style_fields = {'description':'ueditor'}

admin.site.register(MyCourse,MyCourseAdmin)
