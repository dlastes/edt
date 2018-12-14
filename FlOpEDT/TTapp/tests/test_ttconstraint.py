
from django.test import TestCase
from unittest.mock import patch, Mock, call

from base.models import Department, TrainingProgramme, CourseType, Time
from people.models import Tutor
from TTapp.models import LimitCourseTypePerPeriod
from TTapp.TTModel import TTModel


class TTConstraintTestCase(TestCase):

    fixtures = ['dump.json']


    def setUp(self):

        self.info = Department.objects.get(abbrev="info")

        self.dut1 = TrainingProgramme.objects.get(abbrev='INFO1')
        self.dut2 = TrainingProgramme.objects.get(abbrev='INFO2')

        self.DS = CourseType.objects.get(name='CTRL')
        self.CM = CourseType.objects.get(name='CM')
        self.TD = CourseType.objects.get(name='TD')
        self.TP = CourseType.objects.get(name='TP')

        self.c_basic = LimitCourseTypePerPeriod.objects.create(limit=1, type=self.TD, department=self.info)

        self.c_2018 = LimitCourseTypePerPeriod.objects.create(train_prog=self.dut1, year=2018, limit=1, type=self.TD, department=self.info)
        self.c_2018_39 = LimitCourseTypePerPeriod.objects.create(train_prog=self.dut1, year=2018, week=39, limit=0, type=self.TD, department=self.info)
        self.c_2018_39_without_tp = LimitCourseTypePerPeriod.objects.create(year=2018, week=39, limit=0, type=self.TD, department=self.info)

        self.c_tp2 = LimitCourseTypePerPeriod.objects.create(train_prog=self.dut2, limit=0, type=self.TD, department=self.info)
        self.c_2019_1 = LimitCourseTypePerPeriod.objects.create(train_prog=self.dut2, year=2019, week=1, limit=0, type=self.TD, department=self.info)


    def test_constraint_without_training_program(self):   
        view_model = self.c_2018_39_without_tp.get_viewmodel()
        self.assertEqual(view_model['details']['train_prog'], 'All')


    @patch('TTapp.models.LimitCourseTypePerPeriod.register_expression')
    def test_register_expression_without_tutors(self, register_expression):      

        attrs = {'wdb.days': (0,1,2,)}
        ttmodel = Mock(**attrs)

        calls = [
            call(ttmodel, 0, Time.AM, 1.),
            call(ttmodel, 0, Time.PM, 1.),
            call(ttmodel, 1, Time.AM, 1.),
            call(ttmodel, 1, Time.PM, 1.),
            call(ttmodel, 2, Time.AM, 1.),
            call(ttmodel, 2, Time.PM, 1.),            
            ]

        constraint = LimitCourseTypePerPeriod.objects.create(limit=1, type=self.TD, department=self.info)
        constraint.period == LimitCourseTypePerPeriod.FULL_DAY
        constraint.enrich_model(ttmodel)

        register_expression.assert_has_calls(calls)


    @patch('TTapp.models.LimitCourseTypePerPeriod.register_expression')
    def test_register_expression_with_tutors(self, register_expression):      

        constraint = LimitCourseTypePerPeriod.objects.create(limit=1, type=self.TD, department=self.info)
        constraint.period == LimitCourseTypePerPeriod.FULL_DAY

        calls = []
        attrs = {'wdb.days': (0,1,2,)}
        ttmodel = Mock(**attrs)

        for day in ttmodel.wdb.days:
            for period in [Time.AM, Time.PM]:
                for tutor in Tutor.objects.filter(username__in=['AB', 'AJ', 'CDU', 'FMA']):
                    calls.append(call(ttmodel, day, period, 1., tutor=tutor))
                    constraint.tutors.add(tutor)

        constraint.enrich_model(ttmodel)
        register_expression.assert_has_calls(calls)