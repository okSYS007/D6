# Generated by Django 4.0.5 on 2022-07-16 21:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0017_appointment_postid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointment',
            name='postID',
        ),
        migrations.AddField(
            model_name='appointment',
            name='postUrl',
            field=models.TextField(default='/news'),
        ),
    ]