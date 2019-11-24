# Generated by Django 2.1.3 on 2019-11-22 15:32

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0013_auto_20190926_1259'),
        ('base', '0038_auto_20191108_1448'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoursePossibleTutors',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='base.Course')),
                ('possible_tutors', models.ManyToManyField(blank=True, related_name='shared_possible_courses', to='people.Tutor')),
            ],
        ),
        migrations.CreateModel(
            name='ModulePossibleTutors',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='base.Module')),
                ('possible_tutors', models.ManyToManyField(blank=True, related_name='possible_modules', to='people.Tutor')),
            ],
        ),
        migrations.RemoveField(
            model_name='slot',
            name='day',
        ),
        migrations.RemoveField(
            model_name='slot',
            name='hour',
        ),
        migrations.AddField(
            model_name='scheduledcourse',
            name='tutor',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='taught_scheduled_courses', to='people.Tutor'),
        ),
        migrations.AlterField(
            model_name='group',
            name='name',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='time',
            name='hours',
            field=models.PositiveSmallIntegerField(default=8, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(25)]),
        ),
        migrations.DeleteModel(
            name='Day',
        ),
        migrations.DeleteModel(
            name='Slot',
        ),
    ]
