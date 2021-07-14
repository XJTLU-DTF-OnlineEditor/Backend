from __future__ import unicode_literals


import sqlite3
from django.db import models

class codes(models.Model): #models.Model
    code_id = models.CharField(verbose_name="代码 id",max_length=100)
    code_content = models.TextField(blank=True,
                                    null=True,
                                    verbose_name="代码内容")
    compile_status = models.CharField(max_length=100)
    run_status_time = models.IntegerField()
    run_status_memory = models.IntegerField()
    class meta:
        verbose_name = 'source code'
        verbose_name_plural = 'source codes'

# Create your models here.
