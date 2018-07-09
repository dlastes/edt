# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-09 08:52


import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AvoidBothSlots',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week', models.PositiveSmallIntegerField(default=None, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(52)])),
                ('year', models.PositiveSmallIntegerField(default=None, null=True)),
                ('weight', models.PositiveSmallIntegerField(default=None, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)])),
                ('comment', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Contrainte active?')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LimitCourseTypePerPeriod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week', models.PositiveSmallIntegerField(default=None, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(52)])),
                ('year', models.PositiveSmallIntegerField(default=None, null=True)),
                ('weight', models.PositiveSmallIntegerField(default=None, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)])),
                ('comment', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Contrainte active?')),
                ('limit', models.PositiveSmallIntegerField()),
                ('period', models.CharField(choices=[('fd', 'Full day'), ('hd', 'Half day')], max_length=2)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MinHalfDays',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week', models.PositiveSmallIntegerField(default=None, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(52)])),
                ('year', models.PositiveSmallIntegerField(default=None, null=True)),
                ('weight', models.PositiveSmallIntegerField(default=None, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)])),
                ('comment', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Contrainte active?')),
                ('join2courses', models.BooleanField(default=False, verbose_name='If 2 or 4 courses only, join it?')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MinNonPreferedSlot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week', models.PositiveSmallIntegerField(default=None, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(52)])),
                ('year', models.PositiveSmallIntegerField(default=None, null=True)),
                ('weight', models.PositiveSmallIntegerField(default=None, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)])),
                ('comment', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Contrainte active?')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ReasonableDays',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week', models.PositiveSmallIntegerField(default=None, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(52)])),
                ('year', models.PositiveSmallIntegerField(default=None, null=True)),
                ('weight', models.PositiveSmallIntegerField(default=None, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)])),
                ('comment', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Contrainte active?')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SimultaneousCourses',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week', models.PositiveSmallIntegerField(default=None, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(52)])),
                ('year', models.PositiveSmallIntegerField(default=None, null=True)),
                ('weight', models.PositiveSmallIntegerField(default=None, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)])),
                ('comment', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Contrainte active?')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Stabilize',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week', models.PositiveSmallIntegerField(default=None, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(52)])),
                ('year', models.PositiveSmallIntegerField(default=None, null=True)),
                ('weight', models.PositiveSmallIntegerField(default=None, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)])),
                ('comment', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Contrainte active?')),
                ('general', models.BooleanField(default=False, verbose_name='Stabiliser tout?')),
                ('work_copy', models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
