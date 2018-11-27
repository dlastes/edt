import datetime

from django.db.models import Q
from base.models import ScheduledCourse, RoomGroup, Course, Holiday


def get_period(year):

    # We assume that :
    #   a period starts after the summer holidays (week 40)
    _, period_week_swap, _ = datetime.date(year, 8, 1).isocalendar()

    # TODO : Determine the week period limits based on
    # the first period starts week value
    _, start_week, _ = datetime.date(year, 9, 1).isocalendar()
    _, end_week, _ = datetime.date(year + 1, 6, 30).isocalendar()
    _, max_week, _ = datetime.date(year, 12, 28).isocalendar()

    return (
        (year, tuple(range(start_week, max_week + 1))),
        (year + 1, tuple(range(1, end_week + 1))),
        )

def get_holiday_list(period):
    for year, _ in period:
        for holiday in Holiday.objects.filter(year=year):
            yield year, holiday.week, holiday.day.no

def get_open_days():
    pass

def get_holidays_weeks_for_period(period):
    
    # HACK : Get holidays week list by checking courses scheduling
    for current_year, weeks in period:
        for current_week in weeks:
                if not Course.objects.filter(
                        an=current_year,
                        semaine=current_week).exists():
                    yield current_week

def get_room_activity_by_day(department, year):

    # Return a room occupancy array for a department
    # and a given period. If the period is not ended
    # occupancy is computed until the current week

    # We consider occupancy relatively to the number of
    # days where a room is not occupied

    # year : correponds to the first period year
    period = get_period(year)

    # Get room list 
    rooms = tuple(RoomGroup.objects \
        .filter(types__department = department) \
        .values_list('name', flat=True)
        .distinct())

    # Filter all the scheduled courses for the period
    period_filter = None
    for current_year, weeks in period:
        if period_filter:
            period_filter |= Q(cours__an=current_year) and Q(cours__semaine__in=weeks)
        else:
            period_filter = Q(cours__an=current_year) and Q(cours__semaine__in=weeks)

    scheduled = set(ScheduledCourse.objects \
        .filter(
            period_filter,
            copie_travail=0,
            cours__module__train_prog__department=department) \
        .values_list('room__name', 'cours__an', 'cours__semaine', 'creneau__jour') \
        .distinct())

    # Holidays
    holidays = set(get_holidays_weeks_for_period(period))
    holiday_list = set(get_holiday_list(period))
    
    # TODO : nb_open_days
    all_weeks = set()
    period_weeks = [all_weeks.update(weeks) for _, weeks in period]
    nb_open_days = len(all_weeks - holidays) * 5

    # Get the number of day per room where the room is not utilized
    unused_days_by_room = []
    for room in rooms:

        # Initialize unused count
        room_context = { 'room': room, 'count': 0}
        unused_days_by_room.append(room_context)

        for current_year, weeks in period:
            for current_week in weeks:
                # Skip holidays weeks
                if not current_week in holidays:
                    for week_day in tuple(range(1,6)):

                        # Test if the current day is a holiday
                        if (current_year, current_week, week_day,) in holiday_list:
                            continue
                        
                        # Test if a course has been realised in the 
                        # current room for a given day number
                        room_availability = (room, current_year, current_week, week_day)
                        if not(room_availability in scheduled):
                            room_context['count'] += 1 
        

    return {'open_days':nb_open_days, 'room_activity': unused_days_by_room}
