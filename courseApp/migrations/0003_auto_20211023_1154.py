# Generated by Django 2.2.4 on 2021-10-23 03:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courseApp', '0002_auto_20211021_1842'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='topic',
            name='related_courses',
        ),
        migrations.AlterField(
            model_name='topic',
            name='topic_id',
            field=models.CharField(auto_created=True, max_length=20, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='topic',
            name='topic_title',
            field=models.CharField(max_length=20, verbose_name='Topic title'),
        ),
    ]