from base.models import UserPreference, Day, Slot
from people.models import User, Tutor

from csv import DictReader
from datetime import datetime


def translate_day_label(label):
    return [x for x, y in Day.CHOICES if y == label][0]


def recherche_up(USER_PREFS, day, start_time):
    for e in USER_PREFS:
        if e.day == day and e.start_time == start_time:
            return e
    return None


def csv_reader(path):
    start = datetime.now()
    with open(path, newline='') as f:
        file = DictReader(f)
        prof = User.objects.first()
        an = None
        week = None
        user_prefs = None
        for row in file:
            if an != row['year'] or week != row['week'] or prof.username != row['prof']:
                prof = Tutor.objects.get(username=row['prof'])
                an = row['year']
                week = row['week']
                user_prefs = list(
                    UserPreference.objects.filter(user=prof, an=row['year'], semaine=row['week'])
                        .order_by('day', 'start_time'))
                print(prof, week, an)
            duration = int(row['duration'])
            day = translate_day_label(row['day'])
            start_time = int(row['start_time'])

            up = recherche_up(user_prefs, day, start_time)
            value = int(float(row['value'])) * 2
            print(f"Valeur = {value}")
            if up:
                if up.valeur != value or up.duration != duration:
                    up.valeur = value
                    up.save()
                user_prefs.remove(up)
            else:
                UserPreference(user=prof, an=row['year'], semaine=row['week'],
                               day=day, start_time=start_time, duration=duration,
                               valeur=value).save()
    f.close()
    end = datetime.now()
    print(end - start)
