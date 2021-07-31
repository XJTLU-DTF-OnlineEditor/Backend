"""
课程数据库模型
"""
from typing import NewType
from django.db import models
from DjangoUeditor.models import UEditorField
import django.utils.timezone as timezone

class MyCourse(models.Model):
    COURSE_CHOICES = (
        ('基础课程','基础课程'),
        ('进阶课程','进阶课程'),
        ('数据分析','数据分析'),

    )
    title = models.CharField(max_length= 50, verbose_name='课程标题')
    description = UEditorField(u'内容',
                                default = '',
                                height = 300,
                                width = 1000,
                                # imagePath = 'course/images/', 后续加入课程图像
                                filePath = 'course/files/',   #课程路径添加
                                )
    courseType = models.CharField(choices=COURSE_CHOICES,
                                  max_length=50,
                                  verbose_name='课程类型')
    updateDate = models.DateTimeField(max_length=20, 
                                      default=timezone.now,
                                      verbose_name='更新时间')
    views = models.PositiveIntegerField('浏览量', default=0)

    topic_id = models.CharField(max_length=20, null=True)

    subtopic_id = models.CharField(max_length=20, null=True)
    subtopic_title = models.CharField(max_length=32, null=True)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-updateDate']
        verbose_name = '课程'
        verbose_name_plural = verbose_name
class Topic(models.Model):
    topic_id = models.CharField(primary_key=True, max_length=20)
    topic_title = models.CharField(max_length=20)
    topic_content = models.TextField(null=True) #introduction of the topic
