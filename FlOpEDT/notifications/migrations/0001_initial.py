# Generated by Django 3.0.14 on 2022-04-12 15:15

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BackUpModif',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(53)], verbose_name='Week number')),
                ('year', models.PositiveSmallIntegerField()),
                ('day', models.CharField(choices=[('m', 'monday'), ('tu', 'tuesday'), ('w', 'wednesday'), ('th', 'thursday'), ('f', 'friday'), ('sa', 'saturday'), ('su', 'sunday')], default='m', max_length=2)),
                ('module_abbrev', models.CharField(max_length=100, verbose_name='Abbreviation')),
                ('tutor_username', models.CharField(max_length=150, null=True)),
                ('supp_tutor_usernames', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=10), null=True, size=None)),
                ('start_time', models.PositiveSmallIntegerField()),
                ('room_name', models.CharField(max_length=50, null=True)),
                ('group_name', models.CharField(max_length=100)),
                ('department_abbrev', models.CharField(max_length=7)),
                ('train_prog_name', models.CharField(max_length=50)),
                ('new', models.BooleanField(default=True)),
            ],
        ),
    ]
