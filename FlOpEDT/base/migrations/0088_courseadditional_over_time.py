# Generated by Django 3.0.14 on 2022-07-10 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0087_auto_20220616_1952'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseadditional',
            name='over_time',
            field=models.BooleanField(default=False, verbose_name='Over time'),
        ),
    ]
