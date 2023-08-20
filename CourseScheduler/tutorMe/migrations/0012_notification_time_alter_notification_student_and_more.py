# Generated by Django 4.1.7 on 2023-04-09 17:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutorMe', '0011_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='time',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='notification',
            name='student',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='notification',
            name='tutor',
            field=models.CharField(max_length=100),
        ),
    ]
