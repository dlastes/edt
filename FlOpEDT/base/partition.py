from base.timing import TimeInterval, Day, days_index
from datetime import datetime, timedelta
import copy

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
                {"available" : False, "forbiden" : False}))
        self.add_night_time()

    def add_lunch_break(self, start_time, end_time):
        day = self.intervals[0][0].start
        end_hours = end_time//60
        end_minutes = end_time%60
        start_hours = start_time//60
        start_minutes = start_time%60

        #Manque le dernier jour si self.intervals[0][0].start > self.intervals[len(self.intervals)-1][0].end
        while day < self.intervals[len(self.intervals)-1][0].end:
            self.add_slot(
                TimeInterval(
                    datetime(day.year, day.month, day.day, start_hours, start_minutes, 0),
                    datetime(day.year, day.month, day.day, end_hours, end_minutes, 0)
                ), "lunch_break",
                {"forbiden" : True, "lunch_break": True})
            day = day + timedelta(days = 1)
        return True

    #days_of_week must be consecutive
    def add_week_end(self, days_of_week):
        weekend_days = [day for day in [Day.MONDAY, Day.TUESDAY, Day.WEDNESDAY, Day.THURSDAY, Day.FRIDAY, Day.SATURDAY, Day.SUNDAY] if not (day in days_of_week)]
        weekend_indexes =  [days_index[day] for day in weekend_days]

        i=0
        while weekend_indexes[len(weekend_indexes)-1] - weekend_indexes[0] >= len(weekend_indexes) and i < len(weekend_indexes):
            weekend_indexes.append(weekend_indexes[0]+7)
            weekend_indexes.remove(weekend_indexes[0])
            i+=1
        if weekend_indexes[len(weekend_indexes)-1] - weekend_indexes[0] >= len(weekend_indexes):
            return False
        
        day = self.intervals[0][0].start
        number_of_day_week_end = weekend_indexes[len(weekend_indexes)-1]-weekend_indexes[0]
        #Manque le dernier jour si self.intervals[0][0].start > self.intervals[len(self.intervals)-1][0].end
        while day < self.intervals[len(self.intervals)-1][0].end:
            if day.weekday() == weekend_indexes[0]:
                self.add_slot(
                    TimeInterval(
                        datetime(day.year, day.month, day.day, 0, 0, 0),
                        datetime(day.year, day.month, (day + timedelta(days = number_of_day_week_end+1)).day, 0, 0, 0)
                    ), "week_end",
                    {"forbiden" : True, "week_end": True})
                day = day + timedelta(days = number_of_day_week_end)
            else:
                day = day + timedelta(days = 1)
        return True


    def add_night_time(self):
        #First element of the list of tuples, and the first element of the tuple ie the TimeInterval
        day = self.intervals[0][0].start
        end_hours = self.day_end_time//60
        end_minutes = self.day_end_time%60
        start_hours = self.day_start_time//60
        start_minutes = self.day_start_time%60
        if self.intervals[0][0].start.hour < start_hours or (self.intervals[0][0].start.hour == start_hours
                                                            and self.intervals[0][0].start.minute < start_minutes):
            self.add_slot(TimeInterval(
                datetime(day.year, day.month, day.day, 0, 0, 0),
                datetime(day.year, day.month, day.day, start_hours, start_minutes)
                ), "night_time", {"forbiden" : True, "night_time" : True})
        while day < self.intervals[len(self.intervals)-1][0].end:
            self.add_slot(
                TimeInterval(
                    datetime(day.year, day.month, day.day, end_hours, end_minutes, 0),
                    datetime(day.year, day.month, (day + timedelta(days = 1)).day, start_hours, start_minutes, 0)
                ), "night_time",
                {"forbiden" : True, "night_time": True})
            day = day + timedelta(days = 1)

    def nb_slots_of_duration(self, duration):
        current_duration = 0
        nb_slots = 0
        for interval in self.intervals:
            if interval[1]["available"] and not interval[1]["forbiden"]:
                current_duration += interval[0].duration
            else:
                nb_slots += current_duration//duration
                current_duration = 0
        return int(nb_slots)

    @property
    def day_duration(self):
        return (self.day_end_time - self.day_start_time)

    @property
    def nb_intervals(self):
      return len(self.intervals)

    @property
    def duration(self):
        return abs(self.intervals[len(self.intervals)-1][0].end - self.intervals[0][0].start).total_seconds()//60

    @property
    def available_duration(self):
        avail_duration = 0
        for interval in self.intervals:
            if interval[1]["available"] and not interval[1]["forbiden"]:
                avail_duration += interval[0].duration
        return avail_duration

    @property
    def not_forbiden_duration(self):
        not_forbid = 0
        for interval in self.intervals:
            if not interval[1]["forbiden"]:
                not_forbid += interval[0].duration
        return not_forbid

    def add_data(self, data_type, data, interval_index):
        if "available" in data:
            self.intervals[interval_index][1]["available"] = self.intervals[interval_index][1]["available"] or data["available"]
        if "forbiden" in data:
            self.intervals[interval_index][1]["forbiden"] = self.intervals[interval_index][1]["forbiden"] or data["forbiden"]
        if not data_type in self.intervals[interval_index][1]:
            self.intervals[interval_index][1][data_type] = dict()
        if data_type == "user_preference":
            self.intervals[interval_index][1][data_type][data["tutor"]] = data["value"]
        elif data_type == "night_time" or "lunch_break" or "week_end":
            self.intervals[interval_index][1][data_type] = data[data_type]
            
    def clear_merge(self):
        length = len(self.intervals)-1
        i = 0
        while i < length:
            if self.intervals[i][1] == self.intervals[i+1][1]:
                self.intervals[i][0].end = self.intervals[i+1][0].end
                self.intervals.remove(self.intervals[i+1])
                length-=1
            else:
                i+=1

    #data_type can be:
    #   - "user_preference" : with key "tutor" and "available"
    #   - "night_time" : with key "night_time" and "forbiden"
    #   - "lunch_break" : with key "lunch_break" and "forbiden"
    #   - "week_end" : with key "week_end" and "forbiden"
    def add_slot(self, interval, data_type, data):
        i = 0
        #Check if we are in the interval range
        if (interval.start >= self.intervals[len(self.intervals)-1][0].end
                or interval.end <= self.intervals[0][0].start):
            return False

        while self.intervals[i][0].end <= interval.start:
            i += 1
        
        while i < len(self.intervals) and interval.end > self.intervals[i][0].start:
            if(interval.start == self.intervals[i][0].end):
                i+=1
            if i == 0 and self.intervals[i][0].start > interval.start:
                interval.start = self.intervals[i][0].start
            if i == len(self.intervals)-1 and self.intervals[i][0].end < interval.end:
                interval.end = self.intervals[i][0].end
            #IF WE ALREADY HAVE THE SAME INTERVAL WE APPEND THE DATA
            if self.intervals[i][0] == interval:
                self.add_data(data_type, copy.deepcopy(data), i)
                i += 1
            #IF WE ARE INSIDE AN EXISTING INTERVAL
            elif self.intervals[i][0].start <= interval.start and self.intervals[i][0].end >= interval.end:
                new_part = 1
                if self.intervals[i][0].end != interval.end:
                    self.intervals.insert(i+1, (TimeInterval(interval.end, self.intervals[i][0].end),
                                                            copy.deepcopy(self.intervals[i][1])))
                    self.intervals[i][0].end = interval.end
                if self.intervals[i][0].start != interval.start:
                    self.intervals[i][0].end = interval.start
                    self.intervals.insert(i+1, (TimeInterval(interval.start, interval.end), copy.deepcopy(self.intervals[i][1])))
                    self.add_data(data_type, copy.deepcopy(data), i+1)
                    new_part += 1
                else:
                    self.add_data(data_type, copy.deepcopy(data), i)
                i += new_part
            #ELSE WE ARE IN BETWEEN TWO OR MORE INTERVALS
            else:
                #The TimeInterval at the index i is inside our new TimeInterval
                if self.intervals[i][0].start == interval.start:
                    self.add_data(data_type, copy.deepcopy(data), i)
                    interval.start = self.intervals[i+1][0].start
                #Our new TimeInterval is cut by the ones at the index i and i+1
                elif self.intervals[i][0].end > interval.start:
                    self.intervals[i][0].end = interval.start
                    self.intervals.insert(i+1, (TimeInterval(interval.start, self.intervals[i+1][0].start), copy.deepcopy(self.intervals[i][1])))
                    self.add_data(data_type, copy.deepcopy(data), i+1)
                    i += 2
                    interval.start = self.intervals[i][0].start
        return True