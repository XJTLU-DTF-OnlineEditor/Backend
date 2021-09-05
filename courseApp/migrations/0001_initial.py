# Generated by Django 2.2.4 on 2021-07-31 17:53

import DjangoUeditor.models
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MyCourse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, verbose_name='课程标题')),
                ('description', DjangoUeditor.models.UEditorField(default='', verbose_name='内容')),
                ('topic_name', models.CharField(choices=[('Python3 教程', 'Python3 教程'), ('Python3 高阶教程', 'Python3 高阶教程'), ('Python3 待定', 'Python3 待定')], max_length=50, verbose_name='课程类型')),
                ('update_date', models.DateTimeField(default=django.utils.timezone.now, max_length=20, verbose_name='更新时间')),
                ('views', models.PositiveIntegerField(default=0, verbose_name='浏览量')),
                ('topic_id', models.CharField(choices=[('2', 'Python3 高阶教程'), ('3', 'Python3 待定'), ('1', 'Python3 教程')], max_length=20, null=True, verbose_name='课程类型id')),
                ('subtopic_title', models.CharField(max_length=32, null=True, verbose_name='详细课程标题')),
            ],
            options={
                'verbose_name': '课程',
                'verbose_name_plural': '课程',
                'ordering': ['update_date'],
            },
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('topic_id', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('topic_title', models.CharField(max_length=20)),
                ('topic_content', models.TextField(null=True)),
            ],
        ),
    ]