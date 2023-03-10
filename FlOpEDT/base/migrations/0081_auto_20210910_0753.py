# Generated by Django 3.1.7 on 2021-09-10 07:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0030_auto_20210618_1420'),
        ('base', '0080_dependency_day_gap'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scheduledcourse',
            name='tutor',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='taught_scheduled_courses', to='people.tutor'),
        ),
    ]
