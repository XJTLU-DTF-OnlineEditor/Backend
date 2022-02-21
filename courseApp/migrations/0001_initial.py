# Generated by Django 2.2.4 on 2022-02-21 08:25

import ckeditor_uploader.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('topic_id', models.CharField(auto_created=True, max_length=20, primary_key=True, serialize=False)),
                ('topic_title', models.CharField(max_length=20, verbose_name='Topic title')),
                ('topic_content', models.TextField(null=True)),
                ('views', models.PositiveIntegerField(default=0, verbose_name='浏览量')),
                ('create_time', models.DateTimeField(auto_now=True)),
                ('topic_img', models.ImageField(blank=True, height_field='img_height', null=True, upload_to='', verbose_name='topic_image', width_field='img_width')),
                ('img_width', models.IntegerField(blank=True, null=True, verbose_name='img width')),
                ('img_height', models.IntegerField(blank=True, null=True, verbose_name='img height')),
            ],
        ),
        migrations.CreateModel(
            name='MyCourse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, verbose_name='课程标题')),
                ('description', ckeditor_uploader.fields.RichTextUploadingField(default='请输入课程内容', verbose_name='内容')),
                ('update_date', models.DateTimeField(default=django.utils.timezone.now, max_length=20, verbose_name='更新时间')),
                ('views', models.PositiveIntegerField(default=0, verbose_name='浏览量')),
                ('subtopic_id', models.CharField(max_length=20, unique=True, verbose_name='子类型id')),
                ('related_topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courseApp.Topic')),
            ],
            options={
                'verbose_name': '课程',
                'verbose_name_plural': '课程',
                'ordering': ['update_date'],
            },
        ),
    ]
