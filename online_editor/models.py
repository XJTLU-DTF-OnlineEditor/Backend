from django.db import models


class Codes(models.Model):
    code_id = models.CharField(verbose_name="代码id", max_length=100, unique=True)
    # code_content = models.TextField(blank=True, null=True, verbose_name="代码内容")
    code_result = models.TextField(blank=True, null=True, verbose_name="代码输出结果")
    errors = models.TextField(blank=True, null=True)
    compile_status = models.CharField(max_length=100)
    # run_status_time = models.IntegerField(null=True, default=0)
    # run_status_memory = models.IntegerField(null=True, default=0)
    create_time = models.DateTimeField(null=True, auto_now=True)


class Sources(models.Model):
    code = models.ForeignKey(to=Codes, to_field="code_id", on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    content = models.FileField(blank=True, null=True, verbose_name="代码内容")