# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-18 10:28
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("people", "0015_auto_20170518_1015")]

    operations = [
        migrations.RemoveField(model_name="person", name="elections"),
        migrations.RemoveField(model_name="person", name="posts"),
    ]
