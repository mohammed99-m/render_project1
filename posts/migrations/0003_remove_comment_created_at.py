# Generated by Django 5.1.7 on 2025-05-04 19:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_comment_created_at_post_created_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='created_at',
        ),
    ]
