# Generated by Django 3.1.7 on 2021-06-18 14:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0029_remove_student_belong_to'),
    ]

    operations = [
        migrations.RenameField(
            model_name='student',
            old_name='generic_belong_to',
            new_name='belong_to',
        ),
    ]