from base.timing import TimeInterval
from datetime import datetime, timedelta

class Partition(object):
    #date_start, date_end : datetime
    #day_start_time, day_end_time : int
    def __init__(self, type, date_start, date_end, day_start_time, day_end_time):
        self.intervals = []
        self.type = type
        self.day_start_time = day_start_time
        self.day_end_time = day_end_time
        self.intervals.append(
            (TimeInterval(date_start, date_end),
                {"available" : False, "forbiden" : False},
                []
            )
                            )
        self.add_night_time()

    def add_night_time(self):
        day = self.intervals[0][0].start
        end_hours = self.day_end_time//60
        end_minutes = self.day_end_time%60
        start_hours = self.day_start_time//60
        start_minutes = self.day_start_time%60
        
        while day < self.intervals[len(self.intervals)-1][0].end:
            self.add_slot(
                TimeInterval(
                    datetime(day.year, day.month, day.day, end_hours, end_minutes, 0),
                    datetime(day.year, day.month, (day + timedelta(days = 1)).day, start_hours, start_minutes, 0)
                ),
                {'night_time' : True},
                forbiden=True)
            day = day + timedelta(days = 1)

    @property
    def day_duration(self):
        return (self.day_end_time - self.day_start_time)

    @property
    def nb_intervals(self):
      return len(self.intervals)

    @property
    def duration(self):
        return abs(self.intervals[len(self.intervals)-1][0].end - self.intervals[0][0].start).total_seconds()//60


    def add_slot(self, interval, data, available = False, forbiden = False):
        i = 0
        #Check if we are in the interval range
        if (interval.start >= self.intervals[len(self.intervals)-1][0].end
                or interval.end <= self.intervals[0][0].start):
            return False

        while self.intervals[i][0].end <= interval.start:
            i += 1
        
        while i < len(self.intervals) and interval.end > self.intervals[i][0].start:
            #IF WE ALREADY HAVE THE SAME INTERVAL WE APPEND THE DATA
            if self.intervals[i][0] == interval:
                self.intervals[i][2].append(data.copy())
                #check changes of availability of access#
                self.intervals[i][1]["available"] = self.intervals[i][1]["available"] or available
                self.intervals[i][1]["forbiden"] = self.intervals[i][1]["forbiden"] or forbiden
                #check changes of availability of access#
                i += 1
            #IF WE ARE INSIDE AN EXISTING INTERVAL
            elif self.intervals[i][0].start <= interval.start and self.intervals[i][0].end >= interval.end:
                new_part = 1
                if self.intervals[i][0].end != interval.end:
                    self.intervals.insert(i+1, (TimeInterval(interval.end, self.intervals[i][0].end),
                                                            self.intervals[i][1].copy(),
                                                            self.intervals[i][2].copy()))
                    self.intervals[i][0].end = interval.end
                if self.intervals[i][0].start != interval.start:
                    self.intervals[i][0].end = interval.start
                    self.intervals.insert(i+1, (TimeInterval(interval.start, interval.end),
                                                {
                                                    "available" : self.intervals[i][1]["available"] or available,
                                                    "forbiden" : forbiden or self.intervals[i][1]["forbiden"]
                                                },
                                                self.intervals[i][2][:]+[data.copy()]))
                    new_part += 1
                else:
                    self.intervals[i][2].append(data)
                    #check changes of availability of access#
                    self.intervals[i][1]["available"] = self.intervals[i][1]["available"] or available
                    self.intervals[i][1]["forbiden"] = forbiden or self.intervals[i][1]["forbiden"]
                    #check changes of availability of access#
                i += new_part
            #ELSE WE ARE IN BETWEEN TWO OR MORE INTERVALS
            else:
                if self.intervals[i][0].end > interval.start:
                    self.intervals[i][0].end = interval.start
                    self.intervals.insert(i+1, (TimeInterval(interval.start, self.intervals[i+1][0].start),
                                                {
                                                    "available" : self.intervals[i][1]["available"] or available,
                                                    "forbiden" : forbiden or self.intervals[i][1]["forbiden"]
                                                },
                                                self.intervals[i][2][:]+[data.copy()]))
                    i += 2
                else:
                    self.intervals[i][2].append(data)
                    #check changes of availability of access#
                    self.intervals[i][1]["available"] = self.intervals[i][1]["available"] or available
                    self.intervals[i][1]["forbiden"] = forbiden or self.intervals[i][1]["forbiden"]
                    #check changes of availability of access#
                    i += 1
                interval.start = self.intervals[i][0].start
        return True