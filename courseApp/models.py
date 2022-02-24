"""
课程数据库模型
"""
from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
import django.utils.timezone as timezone

"""
Topic模型还不完善 如有加入需要引用外键
对应课程页面的各个课程卡片
"""


class Topic(models.Model):
    topic_title = models.CharField(max_length=20, verbose_name='Topic title')  # Topic title
    topic_id = models.IntegerField(primary_key=True, auto_created=True, )

    topic_description = models.TextField(max_length=200, default="")  # A brief description of the content

    topic_content = models.TextField(null=True)  # introduction to the main content of the topic
    views = models.PositiveIntegerField('浏览量', default=0)  # view numbers of the topic
    create_time = models.DateTimeField(auto_now=True)
    topic_img = models.ImageField(null=True, width_field='img_width', height_field='img_height',
                                  blank=True, verbose_name='topic_image', upload_to="topic_imgs")
    img_width = models.IntegerField(verbose_name='img width', null=True, blank=True)
    img_height = models.IntegerField(verbose_name='img height', null=True, blank=True)

    def __str__(self):
        return self.topic_title


"""
具体数据库构建由Kiki完成 
其余部分进行了Ueditor的引入和选择方法的简化
"""


class MyCourse(models.Model):
    id = models.IntegerField(primary_key=True, max_length=20, auto_created=True, )
    content = RichTextUploadingField(u'内容', default='请输入课程内容')
    teacher_id = models.CharField(max_length=20, default=None)
    related_topic = models.ForeignKey(to=Topic, on_delete=models.CASCADE)
    title = models.CharField(max_length=50, verbose_name='课程标题')  # 和subtopic_title
    update_date = models.DateTimeField(max_length=20,
                                       default=timezone.now,
                                       verbose_name='更新时间')

    views = models.PositiveIntegerField('浏览量', default=0)

    subtopic_id = models.IntegerField(verbose_name='课程id')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['update_date']  # 设定排序方式也可以以id来进行排序
        verbose_name = '课程'
        verbose_name_plural = verbose_name
