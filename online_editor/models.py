from django.db import models


class Codes(models.Model):  # models.Model
    code_id = models.CharField(verbose_name="代码 id", max_length=100)
    code_content = models.TextField(blank=True,
                                    null=True,
                                    verbose_name="代码内容")
    code_result = models.TextField(blank=True,
                                   null=True,
                                   verbose_name="代码输出结果")
    errors = models.TextField(blank=True,
                              null=True)
    compile_status = models.CharField(max_length=100)
    run_status_time = models.IntegerField(null=True, default=0)
    run_status_memory = models.IntegerField(null=True, default=0)
    create_time = models.DateTimeField(null=True, auto_now=True)



# Create your models here.
