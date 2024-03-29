# Generated by Django 2.2.4 on 2022-04-25 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courseApp', '0003_auto_20220425_2105'),
        ('identity', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='history',
            name='course',
        ),
        migrations.AddField(
            model_name='history',
            name='finished_courses',
            field=models.ManyToManyField(to='courseApp.MyCourse', verbose_name='finished_courses'),
        ),
        migrations.AddField(
            model_name='history',
            name='progress_course',
            field=models.IntegerField(null=True, verbose_name='progress_course_id'),
        ),
    ]
