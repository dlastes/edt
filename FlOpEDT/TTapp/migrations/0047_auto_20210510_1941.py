# Generated by Django 3.0.5 on 2021-05-10 19:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('TTapp', '0046_auto_20210510_1804'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='avoidbothtimes',
            name='week',
        ),
        migrations.RemoveField(
            model_name='avoidbothtimes',
            name='year',
        ),
        migrations.RemoveField(
            model_name='boundphysicalpresencehalfdays',
            name='week',
        ),
        migrations.RemoveField(
            model_name='boundphysicalpresencehalfdays',
            name='year',
        ),
        migrations.RemoveField(
            model_name='breakaroundcoursetype',
            name='week',
        ),
        migrations.RemoveField(
            model_name='breakaroundcoursetype',
            name='year',
        ),
        migrations.RemoveField(
            model_name='considerdepencies',
            name='week',
        ),
        migrations.RemoveField(
            model_name='considerdepencies',
            name='year',
        ),
        migrations.RemoveField(
            model_name='curfew',
            name='week',
        ),
        migrations.RemoveField(
            model_name='curfew',
            name='year',
        ),
        migrations.RemoveField(
            model_name='customconstraint',
            name='week',
        ),
        migrations.RemoveField(
            model_name='customconstraint',
            name='year',
        ),
        migrations.RemoveField(
            model_name='groupslunchbreak',
            name='week',
        ),
        migrations.RemoveField(
            model_name='groupslunchbreak',
            name='year',
        ),
        migrations.RemoveField(
            model_name='limitedroomchoices',
            name='week',
        ),
        migrations.RemoveField(
            model_name='limitedroomchoices',
            name='year',
        ),
        migrations.RemoveField(
            model_name='limitedstarttimechoices',
            name='week',
        ),
        migrations.RemoveField(
            model_name='limitedstarttimechoices',
            name='year',
        ),
        migrations.RemoveField(
            model_name='limitgroupsphysicalpresence',
            name='week',
        ),
        migrations.RemoveField(
            model_name='limitgroupsphysicalpresence',
            name='year',
        ),
        migrations.RemoveField(
            model_name='limitgroupstimeperperiod',
            name='week',
        ),
        migrations.RemoveField(
            model_name='limitgroupstimeperperiod',
            name='year',
        ),
        migrations.RemoveField(
            model_name='limitmodulestimeperperiod',
            name='week',
        ),
        migrations.RemoveField(
            model_name='limitmodulestimeperperiod',
            name='year',
        ),
        migrations.RemoveField(
            model_name='limittutorstimeperperiod',
            name='week',
        ),
        migrations.RemoveField(
            model_name='limittutorstimeperperiod',
            name='year',
        ),
        migrations.RemoveField(
            model_name='lowerboundbusydays',
            name='week',
        ),
        migrations.RemoveField(
            model_name='lowerboundbusydays',
            name='year',
        ),
        migrations.RemoveField(
            model_name='mingroupshalfdays',
            name='week',
        ),
        migrations.RemoveField(
            model_name='mingroupshalfdays',
            name='year',
        ),
        migrations.RemoveField(
            model_name='minimizebusydays',
            name='week',
        ),
        migrations.RemoveField(
            model_name='minimizebusydays',
            name='year',
        ),
        migrations.RemoveField(
            model_name='minmoduleshalfdays',
            name='week',
        ),
        migrations.RemoveField(
            model_name='minmoduleshalfdays',
            name='year',
        ),
        migrations.RemoveField(
            model_name='minnonpreferedtrainprogsslot',
            name='week',
        ),
        migrations.RemoveField(
            model_name='minnonpreferedtrainprogsslot',
            name='year',
        ),
        migrations.RemoveField(
            model_name='minnonpreferedtutorsslot',
            name='week',
        ),
        migrations.RemoveField(
            model_name='minnonpreferedtutorsslot',
            name='year',
        ),
        migrations.RemoveField(
            model_name='mintutorshalfdays',
            name='week',
        ),
        migrations.RemoveField(
            model_name='mintutorshalfdays',
            name='year',
        ),
        migrations.RemoveField(
            model_name='nogroupcourseonday',
            name='week',
        ),
        migrations.RemoveField(
            model_name='nogroupcourseonday',
            name='year',
        ),
        migrations.RemoveField(
            model_name='notutorcourseonday',
            name='week',
        ),
        migrations.RemoveField(
            model_name='notutorcourseonday',
            name='year',
        ),
        migrations.RemoveField(
            model_name='novisio',
            name='week',
        ),
        migrations.RemoveField(
            model_name='novisio',
            name='year',
        ),
        migrations.RemoveField(
            model_name='respectboundperday',
            name='week',
        ),
        migrations.RemoveField(
            model_name='respectboundperday',
            name='year',
        ),
        migrations.RemoveField(
            model_name='simultaneouscourses',
            name='week',
        ),
        migrations.RemoveField(
            model_name='simultaneouscourses',
            name='year',
        ),
        migrations.RemoveField(
            model_name='stabilizationthroughweeks',
            name='week',
        ),
        migrations.RemoveField(
            model_name='stabilizationthroughweeks',
            name='year',
        ),
        migrations.RemoveField(
            model_name='stabilize',
            name='week',
        ),
        migrations.RemoveField(
            model_name='stabilize',
            name='year',
        ),
        migrations.RemoveField(
            model_name='tutorslunchbreak',
            name='week',
        ),
        migrations.RemoveField(
            model_name='tutorslunchbreak',
            name='year',
        ),
        migrations.RemoveField(
            model_name='visioonly',
            name='week',
        ),
        migrations.RemoveField(
            model_name='visioonly',
            name='year',
        ),
    ]
