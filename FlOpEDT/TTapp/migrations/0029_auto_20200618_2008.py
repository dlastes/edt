# Generated by Django 3.0.5 on 2020-06-18 20:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0017_notificationspreferences'),
        ('base', '0056_moduletutorrepartition'),
        ('TTapp', '0028_auto_20200618_2004'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='LimitGroupsCourseTypeTimePerPeriod',
            new_name='LimitGroupsTimePerPeriod',
        ),
        migrations.RenameModel(
            old_name='LimitModulesCourseTypeTimePerPeriod',
            new_name='LimitModulesTimePerPeriod',
        ),
        migrations.RenameModel(
            old_name='LimitTutorsCourseTypeTimePerPeriod',
            new_name='LimitTutorsTimePerPeriod',
        ),
    ]
