# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-24 17:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='slug',
            field=models.CharField(default='', max_length=50),
        ),
    ]
