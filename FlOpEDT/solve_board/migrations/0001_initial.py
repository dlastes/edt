# -*- coding: utf-8 -*-
<<<<<<< Updated upstream
<<<<<<< Updated upstream
# Generated by Django 1.11 on 2018-06-22 21:26
=======
# Generated by Django 1.11.13 on 2018-07-09 05:22
>>>>>>> Stashed changes
=======
# Generated by Django 1.11.13 on 2018-07-09 05:22
>>>>>>> Stashed changes
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SolveRun',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('run_label', models.CharField(max_length=60)),
                ('start_week', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(53)])),
                ('start_year', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('end_week', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(53)])),
                ('end_year', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('log_file', models.CharField(default=None, max_length=1000, null=True)),
                ('iis_file', models.CharField(default=None, max_length=1000, null=True)),
            ],
        ),
    ]
