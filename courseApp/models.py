"""
课程数据库模型
"""
from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from identity.models import Admin


class Topic(models.Model):
    topic_title = models.CharField(max_length=20, verbose_name='Topic title')  # Topic title
    topic_id = models.AutoField(primary_key=True, auto_created=True)
    teacher = models.ForeignKey(to=Admin, on_delete=models.CASCADE)
    topic_description = models.TextField(max_length=200, default="")  # A brief description of the content
    topic_content = models.TextField(null=True)  # introduction to the main content of the topic
    views = models.PositiveIntegerField('浏览量', default=0)  # view numbers of the topic
    create_time = models.DateTimeField(auto_now=True)
    topic_img = models.ImageField(null=True, blank=True, verbose_name='topic_image', upload_to="topic_imgs/")

    def __str__(self):
        return self.topic_title


class MyCourse(models.Model):
    id = models.AutoField(primary_key=True, max_length=20, auto_created=True, unique=True)
    content = RichTextUploadingField(u'内容', default='请输入课程内容')
    related_topic = models.ForeignKey(to=Topic, on_delete=models.CASCADE)
    title = models.CharField(max_length=50, verbose_name='课程标题')  # 和subtopic_title
    update_date = models.DateTimeField(max_length=20,
                                       verbose_name='更新时间',
                                       auto_now=True)
    views = models.PositiveIntegerField('浏览量', default=0)
    subtopic_id = models.IntegerField(verbose_name='课程id')
    hint = models.TextField(blank=True, null=True)
    answer = models.TextField(blank=True, null=True)
    code = models.TextField(blank=True, null=True, verbose_name='骨架代码')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['update_date']  # 设定排序方式也可以以id来进行排序
        verbose_name = '课程'
        verbose_name_plural = verbose_name
