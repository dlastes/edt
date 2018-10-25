from django.test import TestCase

import base.models as models
import base.queries as queries


class FirstDepartmentTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.tp1 = models.TrainingProgramme.objects.create(name="TrainingProgramme1", abbrev="tp1")
        cls.tp2 = models.TrainingProgramme.objects.create(name="TrainingProgramme2", abbrev="tp2")
        cls.edt_version_1 = models.EdtVersion.objects.create(semaine=1, an=2018, version=0)
        cls.edt_version_2 = models.EdtVersion.objects.create(semaine=2, an=2018, version=0)
        
    def test_create_first_department(self):
        department = queries.create_first_department()
        self.assertEqual(department.abbrev, "default")

    def test_updated_training_programme(self):
        # test if all existing training programs have been 
        # updated with the new department reference
        department = queries.create_first_department()
        nb_training_programs = department.trainingprogramme_set.count()
        self.assertEqual(nb_training_programs, models.TrainingProgramme.objects.count())      

    def test_updated_edt_version(self):
        # test if all existing training programs have been 
        # updated with the new department reference
        department = queries.create_first_department()
        nb_edt_version = department.edtversion_set.count()
        self.assertEqual(nb_edt_version, models.EdtVersion.objects.count())                

class EdtVersionTestCase(TestCase):
    def setUp(self):
        self.d1 = models.Department.objects.create(name="departement1", abbrev="d1")
        self.edt2 = models.EdtVersion.objects.create(department=self.d1, semaine=40, an=2018, version=2)

    def test_create_default_value(self):
        version = queries.get_edt_version("d1", 39, 2018, True)
        self.assertEqual(version, 0)

    def test_get_version_exist(self):
        version = queries.get_edt_version("d1", 40, 2018, False)
        self.assertEqual(version, self.edt2.version)

    def test_get_version_not_exist(self):
        with self.assertRaises(models.EdtVersion.DoesNotExist):     
            queries.get_edt_version("d1", 42, 2018, False)

class ScheduledCourseTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.d1 = models.Department.objects.create(name="departement1", abbrev="d1")
        cls.d2 = models.Department.objects.create(name="departement2", abbrev="d2")
        cls.tp1 = models.TrainingProgramme.objects.create(name="TrainingProgramme1", abbrev="tp1", department=cls.d1)
        cls.tp2 = models.TrainingProgramme.objects.create(name="TrainingProgramme2", abbrev="tp2", department=cls.d2)
        cls.gt1 = models.GroupType.objects.create(name="groupe_type_1")
        cls.g1 = models.Group.objects.create(nom="gp1", train_prog=cls.tp1, type=cls.gt1, size=0)
        cls.ct1 = models.CourseType.objects.create(name="CourseType1")
        cls.p1 = models.Period.objects.create(name="annee_complete", starting_week=0, ending_week=53)
        cls.m1 = models.Module.objects.create(nom="module1", abbrev="m1", train_prog=cls.tp1, period=cls.p1)
        cls.c1 = models.Course.objects.create(groupe=cls.g1, semaine=39, an=2018, type=cls.ct1, module=cls.m1)
        cls.d1 = models.Day.objects.create(day=models.Day.MONDAY)
        cls.t1 = models.Time.objects.create()
        cls.s1 = models.Slot.objects.create(jour=cls.d1, heure=cls.t1)
        cls.sc1 = models.ScheduledCourse.objects.create(cours=cls.c1, creneau=cls.s1)

    def test_get_scheduled_courses_with_department(self):   
        count = queries.get_scheduled_courses("d1", 39, 2018, 0).count()
        self.assertEqual(count, 1)
        count = queries.get_scheduled_courses("d2", 39, 2018, 0).count()
        self.assertEqual(count, 0)        