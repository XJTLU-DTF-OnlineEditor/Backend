# Generated by Django 2.2.4 on 2021-08-03 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courseApp', '0004_auto_20210802_2247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mycourse',
            name='topic_id',
            field=models.CharField(choices=[('2', 'Python3 高阶教程'), ('3', 'Python3 待定'), ('1', 'Python3 教程')], max_length=20, null=True, verbose_name='课程类型id'),
        ),
    ]