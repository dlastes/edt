# Generated by Django 3.0.14 on 2022-12-16 14:41

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0091_auto_20221124_2149'),
        ('TTapp', '0073_auto_20221216_1115'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParallelizeCourses',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.PositiveSmallIntegerField(blank=True, default=None, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)])),
                ('title', models.CharField(blank=True, default=None, max_length=30, null=True)),
                ('comment', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active?')),
                ('modified_at', models.DateField(auto_now=True)),
                ('desired_busy_slots_duration', models.PositiveSmallIntegerField(verbose_name='max busy slots duration desired')),
                ('course_types', models.ManyToManyField(blank=True, to='base.CourseType')),
                ('department', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.Department')),
                ('modules', models.ManyToManyField(blank=True, to='base.Module')),
                ('train_progs', models.ManyToManyField(blank=True, to='base.TrainingProgramme')),
                ('weeks', models.ManyToManyField(blank=True, to='base.Week')),
            ],
            options={
                'verbose_name': 'Parallelize courses',
                'verbose_name_plural': 'Parallelize courses',
            },
        ),
    ]
