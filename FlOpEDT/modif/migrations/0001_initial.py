# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-17 18:18
from __future__ import unicode_literals

import caching.base
import colorfield.fields
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BreakingNews',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(53)])),
                ('year', models.PositiveSmallIntegerField()),
                ('x_beg', models.FloatField(blank=True, default=2.0)),
                ('x_end', models.FloatField(blank=True, default=3.0)),
                ('y', models.PositiveSmallIntegerField(blank=True, default=None, null=True)),
                ('txt', models.CharField(max_length=200)),
                ('fill_color', colorfield.fields.ColorField(default='#228B22', max_length=18)),
                ('strk_color', colorfield.fields.ColorField(default='#000000', max_length=18)),
            ],
        ),
        migrations.CreateModel(
            name='Cours',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nature', models.CharField(choices=[('CM', 'Cours magistral'), ('TD', 'Travaux Dirig\xe9s'), ('TP', 'Travaux Pratiques'), ('DS', 'Devoir surveill\xe9')], max_length=2)),
                ('no', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('semaine', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(53)])),
                ('an', models.PositiveSmallIntegerField()),
                ('suspens', models.BooleanField(default=False, verbose_name='En suspens?')),
            ],
            bases=(caching.base.CachingMixin, models.Model),
        ),
        migrations.CreateModel(
            name='CoursModification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semaine_old', models.PositiveSmallIntegerField(null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(53)])),
                ('an_old', models.PositiveSmallIntegerField(null=True)),
                ('version_old', models.PositiveIntegerField()),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cours', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='modif.Cours')),
            ],
        ),
        migrations.CreateModel(
            name='CoursPlace',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('no', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('noprec', models.BooleanField(default=True, verbose_name='vrai si on ne veut pas garder la salle')),
                ('copie_travail', models.PositiveSmallIntegerField(default=0)),
                ('cours', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='modif.Cours')),
            ],
            bases=(caching.base.CachingMixin, models.Model),
        ),
        migrations.CreateModel(
            name='CoutGroupe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semaine', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(53)])),
                ('an', models.PositiveSmallIntegerField()),
                ('valeur', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='CoutProf',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semaine', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(53)])),
                ('an', models.PositiveSmallIntegerField()),
                ('valeur', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Creneau',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            bases=(caching.base.CachingMixin, models.Model),
        ),
        migrations.CreateModel(
            name='DemiJourFeriePromo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('apm', models.CharField(choices=[('AM', 'Matin'), ('PM', 'Apr\xe8s-midi')], default='AM', max_length=2, verbose_name='Demi-journ\xe9e')),
                ('semaine', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(53)])),
                ('an', models.PositiveSmallIntegerField()),
                ('promo', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(2)])),
            ],
        ),
        migrations.CreateModel(
            name='DispoCours',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nature', models.CharField(choices=[('CM', 'Cours magistral'), ('TD', 'Travaux Dirig\xe9s'), ('TP', 'Travaux Pratiques'), ('DS', 'Devoir surveill\xe9')], max_length=2)),
                ('semaine', models.PositiveSmallIntegerField(null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(53)])),
                ('an', models.PositiveSmallIntegerField(null=True)),
                ('valeur', models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
                ('promo', models.PositiveSmallIntegerField(default=1)),
                ('creneau', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='modif.Creneau')),
            ],
        ),
        migrations.CreateModel(
            name='Disponibilite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semaine', models.PositiveSmallIntegerField(null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(53)])),
                ('an', models.PositiveSmallIntegerField(null=True)),
                ('valeur', models.SmallIntegerField(default=10, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
                ('creneau', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='modif.Creneau')),
            ],
        ),
        migrations.CreateModel(
            name='DJLGroupe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semaine', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(53)])),
                ('an', models.PositiveSmallIntegerField()),
                ('DJL', models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='EdtVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semaine', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(53)])),
                ('an', models.PositiveSmallIntegerField()),
                ('version', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Groupe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=4)),
                ('nature', models.CharField(choices=[('to', 'Classe enti\xe8re'), ('TD', 'Groupe TD'), ('TP', 'Groupe TP')], max_length=2, verbose_name='Type de classe')),
                ('taille', models.PositiveSmallIntegerField()),
                ('promo', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(3)])),
                ('basic', models.BooleanField(default=False, verbose_name='Basic group?')),
                ('surgroupe', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='modif.Groupe')),
            ],
        ),
        migrations.CreateModel(
            name='Heure',
            fields=[
                ('apm', models.CharField(choices=[('AM', 'Matin'), ('PM', 'Apr\xe8s-midi')], default='AM', max_length=2, verbose_name='Demi-journ\xe9e')),
                ('no', models.PositiveSmallIntegerField(primary_key=True, serialize=False)),
                ('nom', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Jour',
            fields=[
                ('no', models.PositiveSmallIntegerField(primary_key=True, serialize=False, verbose_name='Num\xe9ro')),
                ('nom', models.CharField(max_length=10, verbose_name='Nom')),
            ],
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=50, null=True)),
                ('abbrev', models.CharField(max_length=10, verbose_name='Intitul\xe9 abbr\xe9g\xe9')),
                ('ppn', models.CharField(default='M', max_length=5)),
                ('promo', models.PositiveSmallIntegerField(default=1)),
                ('nbTD', models.PositiveSmallIntegerField(default=1)),
                ('nbTP', models.PositiveSmallIntegerField(default=1)),
                ('nbCM', models.PositiveSmallIntegerField(default=1)),
                ('nbDS', models.PositiveSmallIntegerField(default=1)),
                ('responsable', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PlanifModification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semaine_old', models.PositiveSmallIntegerField(null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(53)])),
                ('an_old', models.PositiveSmallIntegerField(null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cours', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='modif.Cours')),
                ('prof_old', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='old_p', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modif', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Precede',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('successifs', models.BooleanField(default=False, verbose_name='Successifs?')),
                ('ND', models.BooleanField(default=False, verbose_name='Jours differents')),
                ('cours1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cours1', to='modif.Cours')),
                ('cours2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cours2', to='modif.Cours')),
            ],
        ),
        migrations.CreateModel(
            name='Prof',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pref_slots_per_day', models.PositiveSmallIntegerField(default=4, verbose_name='Combien de cr\xe9neaux par jour au mieux ?')),
                ('rights', models.PositiveSmallIntegerField(default=0, verbose_name='Peut forcer ?')),
                ('statut', models.CharField(choices=[('Vac', 'Vacataire'), ('FuS', 'Permanent UT2J (IUT ou non)'), ('BIA', 'BIATOS')], default='FuS', max_length=3)),
                ('LBD', models.PositiveSmallIntegerField(default=2, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(4)], verbose_name='Limitation du nombre de jours')),
            ],
        ),
        migrations.CreateModel(
            name='Regen',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semaine', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(53)])),
                ('an', models.PositiveSmallIntegerField()),
                ('full', models.BooleanField(default=True, verbose_name='Compl\xe8te')),
                ('fday', models.PositiveSmallIntegerField(default=1, verbose_name='Jour')),
                ('fmonth', models.PositiveSmallIntegerField(default=1, verbose_name='Mois')),
                ('fyear', models.PositiveSmallIntegerField(default=1, verbose_name='Ann\xe9e')),
                ('stabilize', models.BooleanField(default=False, verbose_name='Stabilis\xe9e')),
                ('sday', models.PositiveSmallIntegerField(default=1, verbose_name='Jour')),
                ('smonth', models.PositiveSmallIntegerField(default=1, verbose_name='Mois')),
                ('syear', models.PositiveSmallIntegerField(default=1, verbose_name='Ann\xe9e')),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
            bases=(caching.base.CachingMixin, models.Model),
        ),
        migrations.CreateModel(
            name='RoomGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
            bases=(caching.base.CachingMixin, models.Model),
        ),
        migrations.CreateModel(
            name='RoomPreference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='RoomType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
            bases=(caching.base.CachingMixin, models.Model),
        ),
        migrations.CreateModel(
            name='RoomUnavailability',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semaine', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(53)])),
                ('an', models.PositiveSmallIntegerField()),
                ('creneau', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='modif.Creneau')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='modif.Room')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='modif.Groupe')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BIATOS',
            fields=[
                ('prof_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='modif.Prof')),
            ],
            bases=('modif.prof',),
        ),
        migrations.CreateModel(
            name='FullStaff',
            fields=[
                ('prof_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='modif.Prof')),
                ('departement', models.CharField(default='INFO', max_length=50)),
                ('is_iut', models.BooleanField(default=True)),
            ],
            bases=('modif.prof',),
        ),
        migrations.CreateModel(
            name='Vacataire',
            fields=[
                ('prof_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='modif.Prof')),
                ('employer', models.CharField(max_length=50, null=True, verbose_name='Employeur ?')),
                ('qualite', models.CharField(max_length=50, null=True)),
                ('field', models.CharField(max_length=50, null=True, verbose_name='Domaine ?')),
            ],
            bases=('modif.prof',),
        ),
        migrations.AddField(
            model_name='roompreference',
            name='for_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='modif.RoomType'),
        ),
        migrations.AddField(
            model_name='roompreference',
            name='prefer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='modif.RoomGroup'),
        ),
        migrations.AddField(
            model_name='roompreference',
            name='unprefer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='modif.RoomGroup'),
        ),
        migrations.AddField(
            model_name='roomgroup',
            name='types',
            field=models.ManyToManyField(blank=True, related_name='members', to='modif.RoomType'),
        ),
        migrations.AddField(
            model_name='room',
            name='subroom_of',
            field=models.ManyToManyField(blank=True, related_name='subrooms', to='modif.RoomGroup'),
        ),
        migrations.AddField(
            model_name='prof',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='proff', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='djlgroupe',
            name='groupe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='modif.Groupe'),
        ),
        migrations.AddField(
            model_name='disponibilite',
            name='prof',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='modif.Prof'),
        ),
        migrations.AddField(
            model_name='demijourferiepromo',
            name='jour',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='modif.Jour'),
        ),
        migrations.AddField(
            model_name='creneau',
            name='heure',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='modif.Heure'),
        ),
        migrations.AddField(
            model_name='creneau',
            name='jour',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='modif.Jour'),
        ),
        migrations.AddField(
            model_name='coutprof',
            name='prof',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='modif.Prof'),
        ),
        migrations.AddField(
            model_name='coutgroupe',
            name='groupe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='modif.Groupe'),
        ),
        migrations.AddField(
            model_name='coursplace',
            name='creneau',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='modif.Creneau'),
        ),
        migrations.AddField(
            model_name='coursplace',
            name='room',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='modif.RoomGroup'),
        ),
        migrations.AddField(
            model_name='coursmodification',
            name='creneau_old',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='modif.Creneau'),
        ),
        migrations.AddField(
            model_name='coursmodification',
            name='room_old',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='modif.RoomGroup'),
        ),
        migrations.AddField(
            model_name='coursmodification',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cours',
            name='groupe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='modif.Groupe'),
        ),
        migrations.AddField(
            model_name='cours',
            name='module',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='module', to='modif.Module'),
        ),
        migrations.AddField(
            model_name='cours',
            name='modulesupp',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modulesupp', to='modif.Module'),
        ),
        migrations.AddField(
            model_name='cours',
            name='prof',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='proprof', to='modif.Prof'),
        ),
        migrations.AddField(
            model_name='cours',
            name='profsupp',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profsupp', to='modif.Prof'),
        ),
        migrations.AddField(
            model_name='cours',
            name='room_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='modif.RoomType'),
        ),
    ]
