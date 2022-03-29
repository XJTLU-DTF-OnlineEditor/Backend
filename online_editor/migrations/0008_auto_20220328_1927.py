# Generated by Django 2.2.4 on 2022-03-28 11:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('online_editor', '0007_auto_20220328_1247'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sources',
            name='code_id',
        ),
        migrations.AddField(
            model_name='sources',
            name='code',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='online_editor.Codes', to_field='code_id'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='sources',
            name='content',
            field=models.FileField(blank=True, null=True, upload_to='', verbose_name='代码内容'),
        ),
    ]