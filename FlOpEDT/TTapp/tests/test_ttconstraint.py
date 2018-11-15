
import base.models as base

from django.test import TestCase
from TTapp.models import LimitCourseTypePerPeriod

class TTConstraintTestCase(TestCase):

    def setUp(self):
        base.Department.objects.all().delete()

        self.department1 = base.Department.objects.create(name="departement1", abbrev="dept1")
        self.department2 = base.Department.objects.create(name="departement2", abbrev="dept2")
        self.tp1 = base.TrainingProgramme.objects.create(name="TrainingProgramme1", abbrev="tp1", department=self.department1)
        self.tp2 = base.TrainingProgramme.objects.create(name="TrainingProgramme2", abbrev="tp2", department=self.department2)
        self.ct1 = base.CourseType.objects.create(name="CourseType1")

        self.c_basic = LimitCourseTypePerPeriod.objects.create(limit=0, type=self.ct1, department=self.department1)

        self.c_2018 = LimitCourseTypePerPeriod.objects.create(train_prog=self.tp1, year=2018, limit=0, type=self.ct1, department=self.department1)
        self.c_2018_39 = LimitCourseTypePerPeriod.objects.create(train_prog=self.tp1, year=2018, week=39, limit=0, type=self.ct1, department=self.department1)
        self.c_2018_39_without_tp = LimitCourseTypePerPeriod.objects.create(year=2018, week=39, limit=0, type=self.ct1, department=self.department1)

        self.c_tp2 = LimitCourseTypePerPeriod.objects.create(train_prog=self.tp2, limit=0, type=self.ct1, department=self.department1)
        self.c_2019_1 = LimitCourseTypePerPeriod.objects.create(train_prog=self.tp2, year=2019, week=1, limit=0, type=self.ct1, department=self.department1)


    def test_constraint_without_training_program(self):   
        view_model = self.c_2018_39_without_tp.get_viewmodel()
        self.assertEqual(view_model['train_prog'], 'All')