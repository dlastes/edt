# Generated by Django 3.0.14 on 2022-11-16 18:09

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0090_auto_20221003_2043'),
        ('people', '0036_notificationspreferences_notify_other_user_modifications'),
        ('TTapp', '0066_auto_20221018_0704'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotAloneForTheseCouseTypes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.PositiveSmallIntegerField(blank=True, default=None, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)])),
                ('title', models.CharField(blank=True, default=None, max_length=30, null=True)),
                ('comment', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active?')),
                ('modified_at', models.DateField(auto_now=True)),
                ('course_types', models.ManyToManyField(blank=True, to='base.CourseType')),
                ('department', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.Department')),
                ('guide_tutors', models.ManyToManyField(blank=True, related_name='not_alone_as_guide', to='people.Tutor', verbose_name='guide tutors')),
                ('modules', models.ManyToManyField(blank=True, to='base.Module')),
                ('train_progs', models.ManyToManyField(blank=True, to='base.TrainingProgramme')),
                ('tutors', models.ManyToManyField(blank=True, related_name='not_alone_as_tutor', to='people.Tutor', verbose_name='tutors')),
                ('weeks', models.ManyToManyField(blank=True, to='base.Week')),
            ],
            options={
                'verbose_name': 'Not alone for those course types',
                'verbose_name_plural': 'Not alone for those course types',
            },
        ),
    ]
