from django.db import models

from courseApp.models import MyCourse


class Codes(models.Model):
    code_id = models.CharField(verbose_name="代码id", max_length=100, unique=True)
    code_result = models.TextField(blank=True, null=True, verbose_name="代码输出结果")
    errors = models.TextField(blank=True, null=True)
    compile_status = models.CharField(max_length=100)
    create_time = models.DateTimeField(null=True, auto_now=True)
    course = models.ForeignKey(to=MyCourse, on_delete=models.CASCADE)
    # user_id = models.ForeignKey(to=U)


class Sources(models.Model):
    code = models.ForeignKey(to=Codes, to_field="code_id", on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    content = models.TextField(blank=True, null=True, verbose_name="代码内容")