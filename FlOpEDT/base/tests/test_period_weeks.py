from django.test import TestCase
from base.core.period_weeks import PeriodWeeks

class PeriodWeeksTestCase(TestCase):   
   
    def test_school_year_2018(self):
        period_2018 = (
            (2018, {35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52}),
            (2019, {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26}))
        
        sy = PeriodWeeks(year=2018)

        for index, (year, weeks) in enumerate(sy):
            self.assertEqual(period_2018[index][0], year)
            self.assertSetEqual(period_2018[index][1], weeks)

        self.assertEqual(sy.start_week, 35)
        self.assertEqual(sy.end_week, 26)

    def test_Q_filter_week_35(self):
        sy = PeriodWeeks(year=2018)
        filter_35 = sy.get_filter(week=35)
        self.assertEqual(str(filter_35), "(AND: ('cours__an', 2018), ('cours__semaine__in', {35}))")

    def test_Q_filter_week_all(self):
        sy = PeriodWeeks(year=2018)
        filter_all = sy.get_filter()
        self.assertEqual(str(filter_all), "(OR: (AND: ('cours__an', 2018), ('cours__semaine__in', {35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52})), (AND: ('cours__an', 2019), ('cours__semaine__in', {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26})))")

         