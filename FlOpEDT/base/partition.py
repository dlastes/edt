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
                {"available" : False, "forbiden" : False}))
        #self.add_night_time()

    def add_night_time(self):
        #First element of the list of tuples, and the first element of the tuple ie the TimeInterval
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
                ), "night_time",
                {"forbiden" : True, "night_time": True})
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

    @property
    def available_duration(self):
        avail_duration = 0
        for interval in self.intervals:
            if interval[1]["available"] and not interval[1]["forbiden"]:
                avail_duration += interval[0].duration
        return avail_duration

    def add_data(self, data_type, data, interval_index):
        if "available" in data:
            self.intervals[interval_index][1]["available"] = self.intervals[interval_index][1]["available"] or data["available"]
        if "forbiden" in data:
            self.intervals[interval_index][1]["forbiden"] = self.intervals[interval_index][1]["forbiden"] or data["forbiden"]
        if not data_type in self.intervals[interval_index][1]:
            self.intervals[interval_index][1][data_type] = dict()
        if data_type == "user_preference":
            self.intervals[interval_index][1][data_type][data["tutor"]] = data["value"]
        elif data_type == "night_time":
            self.intervals[interval_index][1][data_type] = data[data_type]
            

    #data_type can be:
    #   - "user_preference" : with key "tutor", "value" and "available"
    #   - "night_time" : with keys "value" and "forbiden"
    def add_slot(self, interval, data_type, data):
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
                if self.intervals[i][0].end > interval.start:
                    self.intervals[i][0].end = interval.start
                    self.intervals.insert(i+1, (TimeInterval(interval.start, self.intervals[i+1][0].start), copy.deepcopy(self.intervals[i][1])))
                    self.add_data(data_type, copy.deepcopy(data), i+1)
                    i += 2
                else:
                    self.add_data(data_type, copy.deepcopy(data), i)
                    i += 1
                interval.start = self.intervals[i][0].start
        return True