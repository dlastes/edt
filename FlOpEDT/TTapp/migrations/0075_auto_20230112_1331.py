# Generated by Django 3.0.14 on 2023-01-12 13:31

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0036_notificationspreferences_notify_other_user_modifications'),
        ('base', '0091_auto_20221124_2149'),
        ('TTapp', '0074_parallelizecourses'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='RespectMinHoursPerDay',
            new_name='RespectTutorsMinHoursPerDay',
        ),
        migrations.AlterModelOptions(
            name='respecttutorsminhoursperday',
            options={'verbose_name': 'Respect tutors min hours per day bounds', 'verbose_name_plural': 'Respect tutors min hours per day bounds'},
        ),
        migrations.CreateModel(
            name='GroupsMinHoursPerDay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.PositiveSmallIntegerField(blank=True, default=None, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)])),
                ('title', models.CharField(blank=True, default=None, max_length=30, null=True)),
                ('comment', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active?')),
                ('modified_at', models.DateField(auto_now=True)),
                ('min_hours', models.PositiveSmallIntegerField()),
                ('weekdays', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('m', 'monday'), ('tu', 'tuesday'), ('w', 'wednesday'), ('th', 'thursday'), ('f', 'friday'), ('sa', 'saturday'), ('su', 'sunday')], max_length=2), blank=True, null=True, size=None)),
                ('department', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.Department')),
                ('groups', models.ManyToManyField(blank=True, to='base.StructuralGroup')),
                ('train_progs', models.ManyToManyField(blank=True, to='base.TrainingProgramme')),
                ('weeks', models.ManyToManyField(blank=True, to='base.Week')),
            ],
            options={
                'verbose_name': 'Respect groups min hours per day bounds',
                'verbose_name_plural': 'Respect groups min hours per day bounds',
            },
        ),
    ]
