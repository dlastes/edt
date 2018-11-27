from django.test import TestCase
from django.core.management import call_command

import base.models as models
from base.core.statistics import    get_room_activity_by_day, \
                                    get_holidays_weeks_for_period, \
                                    get_holiday_list, \
                                    get_period

class StatisticsRoomTestCase(TestCase):

    fixtures = ['dump.json']

    @classmethod
    def setUpTestData(cls):
        call_command('migrate')

    def test_room_occupancy_rate(self):
        department = models.Department.objects.get(pk=1)
        get_room_activity_by_day(department, 2018)
        self.assertTrue(True)

    def test_get_holidays_weeks_for_period(self):
        period = get_period(2018)
        holidays = list(get_holidays_weeks_for_period(period))
        self.assertIn(44, holidays)

    def test_get_holiday_list(self):
        # May, 1, 2019
        wednesday, _ = models.Day.objects.get_or_create(day=models.Day.WEDNESDAY)
        holiday, _ = models.Holiday.objects.get_or_create(year=2019, week=19, day=wednesday)
        period = get_period(2018)
        holiday_list = list(get_holiday_list(period))
        self.assertIn((holiday.year, holiday.week, holiday.day.no), holiday_list)

    def test_get_period_2018(self):
        period_2018 = (
            (2018, (35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52)),
            (2019, (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26)))
        
        period = get_period(2018)
        self.assertTupleEqual(period, period_2018)

    