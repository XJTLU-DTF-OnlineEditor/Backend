"""
课程数据库模型
"""

from django.db import models
from DjangoUeditor.models import UEditorField
import django.utils.timezone as timezone
"""
具体数据库构建由Kiki完成 
其余部分进行了Ueditor的引入和选择方法的简化
"""
class MyCourse(models.Model):
    COURSE_CHOICES = ( #提供选择选项后续如需加入新的课程只需添加对应名称前面对应数据库后面对应views可减少因打字输入造成的错误
        ('Python3 教程','Python3 教程'),
        ('Python3 高阶教程','Python3 高阶教程'),
        ('Python3 待定','Python3 待定'),

    )
    
    COURSE_ID_CHOICES = {
        ('1','Python3 教程'),
        ('2','Python3 高阶教程'),#同上进行id索引方便调度
        ('3','Python3 待定'),

    }
    title = models.CharField(max_length= 50, verbose_name='课程标题') #和subtopic_title
    description = UEditorField(u'内容',
                                default = '请输入课程内容', 
                                height = 300, #限定长宽可随意更改
                                width = 1000, 
                                # imagePath = 'course/images/', 后续加入课程图像
                                filePath = 'course/files/',   #课程路径添加
                                )
    topic_name = models.CharField(choices=COURSE_CHOICES,
                                  max_length=50,
                                  verbose_name='课程类型')
    update_date = models.DateTimeField(max_length=20, 
                                      default=timezone.now, 
                                      verbose_name='更新时间')
    views = models.PositiveIntegerField('浏览量', default=0)

    topic_id = models.CharField(choices=COURSE_ID_CHOICES, #捆绑topic_name的具体id
                                max_length=20,
                                null=True,
                                verbose_name='课程类型id')

    subtopic_id = models.CharField(max_length=20, null=True,
                                    verbose_name='子类型id') #当前版本和上述id一致
    # subtopic_title = models.CharField(max_length=32, null=True,
    #                                 verbose_name='详细课程标题')

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['update_date'] #设定排序方式也可以以id来进行排序
        verbose_name = '课程'
        verbose_name_plural = verbose_name
"""
Topic模型还不完善 如有加入需要引用外键
"""
class Topic(models.Model):
    topic_id = models.CharField(primary_key=True, max_length=20)
    topic_title = models.CharField(max_length=20)
    topic_content = models.TextField(null=True) #introduction the main content of the topic 
