# Generated by Django 3.1.12 on 2024-11-21 01:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_auto_20241120_2039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='members',
            field=models.TextField(default='[]'),
        ),
        migrations.AlterField(
            model_name='task',
            name='created_by',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='task',
            name='department',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]