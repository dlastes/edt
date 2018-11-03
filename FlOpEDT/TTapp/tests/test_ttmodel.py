
import base.models as models

from django.test import TestCase
from TTapp.TTModel import WeekDB, TTModel

class TTModelTestCase(TestCase):

    fixtures = ['base.json']

    # @classmethod
    # def setUpTestData(cls):
    #     cls.department1 = models.Department.objects.create(name="departement1", abbrev="dept1")
    #     cls.department2 = models.Department.objects.create(name="departement2", abbrev="dept2")
    #     cls.tp1 = models.TrainingProgramme.objects.create(name="TrainingProgramme1", abbrev="tp1", department=cls.department1)
    #     cls.tp2 = models.TrainingProgramme.objects.create(name="TrainingProgramme2", abbrev="tp2", department=cls.department2)
    #     cls.rt1 = models.RoomType(name="rt1",  department=cls.department1)
    #     cls.rt1.save()
    #     cls.rg1 = models.RoomGroup(name="rg1")
    #     cls.rg1.save()
    #     cls.rg1.types.add(cls.rt1)
    #     cls.room1 = models.Room(name="room1")
    #     cls.room1.save()
    #     cls.room1.subroom_of.add(cls.rg1)
    #     cls.gt1 = models.GroupType.objects.create(name="groupe_type_1")
    #     cls.g1 = models.Group.objects.create(nom="gp1", train_prog=cls.tp1, type=cls.gt1, size=0)
    #     cls.ct1 = models.CourseType.objects.create(name="CourseType1")
    #     cls.p1 = models.Period.objects.create(name="annee_complete", starting_week=0, ending_week=53)
    #     cls.m1 = models.Module.objects.create(nom="module1", abbrev="m1", train_prog=cls.tp1, period=cls.p1)
    #     cls.c1 = models.Course.objects.create(groupe=cls.g1, semaine=39, an=2018, type=cls.ct1, module=cls.m1)
    #     cls.day1 = models.Day.objects.create(day=models.Day.MONDAY)
    #     cls.t1 = models.Time.objects.create()
    #     cls.s1 = models.Slot.objects.create(jour=cls.day1, heure=cls.t1)
    #     cls.sc1 = models.ScheduledCourse.objects.create(cours=cls.c1, creneau=cls.s1)

    def test_init(self):   
        tp1 = models.TrainingProgramme.objects.get(abbrev="INFO1")
        tt = TTModel(tp1.department.abbrev, 39, 2018, train_prog=tp1)
        self.assertEqual(True, False)
        # self.assertEqual(list(wdb.room_groups_for_type[self.rt1]), [self.rg1])        