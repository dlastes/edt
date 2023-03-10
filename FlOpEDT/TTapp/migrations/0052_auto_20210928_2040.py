# Generated by Django 3.1.7 on 2021-09-28 20:40

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0030_auto_20210618_1420'),
        ('base', '0081_auto_20210910_0753'),
        ('TTapp', '0051_assignallcourses_pre_assigned_only'),
    ]

    operations = [
        migrations.CreateModel(
            name='StabilizeGroupsCourses',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.PositiveSmallIntegerField(blank=True, default=None, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)])),
                ('comment', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active?')),
                ('modified_at', models.DateField(auto_now=True)),
                ('work_copy', models.PositiveSmallIntegerField(default=0)),
                ('fixed_days', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('m', 'monday'), ('tu', 'tuesday'), ('w', 'wednesday'), ('th', 'thursday'), ('f', 'friday'), ('sa', 'saturday'), ('su', 'sunday')], max_length=2), blank=True, null=True, size=None)),
                ('department', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.department')),
                ('groups', models.ManyToManyField(blank=True, to='base.StructuralGroup')),
                ('train_progs', models.ManyToManyField(blank=True, to='base.TrainingProgramme')),
                ('weeks', models.ManyToManyField(blank=True, to='base.Week')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StabilizeTutorsCourses',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.PositiveSmallIntegerField(blank=True, default=None, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)])),
                ('comment', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active?')),
                ('modified_at', models.DateField(auto_now=True)),
                ('work_copy', models.PositiveSmallIntegerField(default=0)),
                ('fixed_days', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('m', 'monday'), ('tu', 'tuesday'), ('w', 'wednesday'), ('th', 'thursday'), ('f', 'friday'), ('sa', 'saturday'), ('su', 'sunday')], max_length=2), blank=True, null=True, size=None)),
                ('department', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.department')),
                ('train_progs', models.ManyToManyField(blank=True, to='base.TrainingProgramme')),
                ('tutors', models.ManyToManyField(blank=True, to='people.Tutor')),
                ('weeks', models.ManyToManyField(blank=True, to='base.Week')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.DeleteModel(
            name='Stabilize',
        ),
    ]
