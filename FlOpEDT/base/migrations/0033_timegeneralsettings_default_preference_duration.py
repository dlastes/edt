# Generated by Django 2.1.3 on 2019-06-06 23:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0032_auto_20190424_1054'),
    ]

    operations = [
        migrations.AddField(
            model_name='timegeneralsettings',
            name='default_preference_duration',
            field=models.PositiveSmallIntegerField(default=90),
        ),
    ]