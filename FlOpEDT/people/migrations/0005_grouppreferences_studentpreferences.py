# Generated by Django 2.1.4 on 2019-03-02 22:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0017_auto_20190120_1719'),
        ('people', '0005_auto_20190116_2204'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupPreferences',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('morning_weight', models.DecimalField(blank=True, decimal_places=2, default=1, max_digits=3)),
                ('free_half_day_weight', models.DecimalField(blank=True, decimal_places=2, default=1, max_digits=3)),
                ('group', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='groupPreferences', to='base.Group')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StudentPreferences',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('morning_weight', models.DecimalField(blank=True, decimal_places=2, default=1, max_digits=3)),
                ('free_half_day_weight', models.DecimalField(blank=True, decimal_places=2, default=1, max_digits=3)),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='studentPreferences', to='people.Student')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
