import datetime
from django.db.models import Q

class PeriodWeeks():

    """
    Week oriented school year description
    """    
    def __init__(self, year=None, start=None, end=None):

        # school year
        self.start_year = year
        self.end_year = year + 1

        # TODO : ensure that start.year corresponds to year 

        # By default, we assume that a school year starts at 
        # september, 1 and ends at juny, 30
        self.start_day = start if start else datetime.date(self.start_year, 9, 1)
        self.end_day = end if end else datetime.date(self.end_year, 6, 30)

        _, self.start_week, _ = self.start_day.isocalendar()
        _, self.end_week, _ = self.end_day.isocalendar()

        # Get the correct last year week number (52 or 53)
        _, self.max_week, _ = datetime.date(year, 12, 28).isocalendar()

        self.__period_raw = (
            (self.start_year, set(range(self.start_week, self.max_week + 1))),
            (self.end_year, set(range(1, self.end_week + 1))),
            )

        self.__period_weeks = self.__period_raw[0][1] | self.__period_raw[1][1]

    
    def __iter__(self):
        self.current_year_index = 0
        return self

    def __next__(self):
        index = self.current_year_index
        self.current_year_index += 1

        if index < len(self.__period_raw):
            return self.__period_raw[index]
        else:
            raise StopIteration

    def __str__(self):
        return f"School year {self.start_year}-{self.end_year}"            


    def get_default_limits(self):
        start = datetime.date(self.start_year, 9, 1)
        end = datetime.date(self.end_year, 6, 30)
        return (start, end)
        
    def get_weeks(self, year=None):

        weeks = None
        if year and year == self.start_year:
            weeks = self.__period_raw[0][1]
        elif year and year == self.end_year:
            weeks = self.__period_raw[1][1]
        else:
            weeks = self.__period_raw[0][1] | self.__period_raw[1][1]

        return weeks

    
    def get_raw(self):
        return self.__period_raw

    
    def get_filter(self, related_path='cours', week=None):
        """
        Return a Q filter to restrict records returned 
        by course query to a given period
        """
        filter = None
        for year, weeks in self.__period_raw:
            
            week_list = None
            
            if week:
                if week in weeks:
                    week_list = {week}
            else:
                week_list = weeks

            if week_list:
                kwargs = { f"{related_path}__an": year, f"{related_path}__semaine__in": week_list}

                if filter:
                    filter |= Q(**kwargs)
                else:
                    filter = Q(**kwargs)
        
        return filter
