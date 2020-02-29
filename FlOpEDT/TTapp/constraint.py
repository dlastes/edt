def singular_or_plurial(myList, isMale):
    determinant = "les" if len(myList) > 1 else ("le" if isMale else "la")
    conjugation = "s" if len(myList) > 1 else ""
    return determinant, conjugation

def list2str(myList):
    if len(myList) == 1:
        return myList[0]

    output = "["
    for i in range(len(myList) - 1):
        output += myList[i] + ", "
    return output + myList[-1] + "]"

class Constraint:
    def __init__(self, id, constraint_type=None, instructors=[], slots=[], courses=[], weeks=[], rooms=[],
                 groups=[], days=[]):
        self.id = id
        self.constraint_type = constraint_type

        if type(instructors) is not list:
            instructors = [instructors]
        self.instructors = instructors
        if type(slots) is not list:
            slots = [slots]
        self.slots = slots
        if type(courses) is not list:
            courses = [courses]
        self.courses = courses
        if type(weeks) is not list:
            weeks = [weeks]
        self.weeks = weeks
        if type(rooms) is not list:
            rooms = [rooms]
        self.rooms = rooms
        if type(groups) is not list:
            groups = [groups]
        self.groups = groups
        if type(days) is not list:
            days = [days]
        self.days = days

    def get_id(self):
        return self.id

    def __str__(self):
        res = "(%s) La contrainte " % self.id
        if self.constraint_type is not None:
            res += 'de type "%s" ; ' % str(self.constraint_type)

        if len(self.instructors) >= 1:
            d, c = singular_or_plurial(self.instructors, isMale=True)
            res += "pour %s professeur%s %s ; " % (d, c, list2str([str(instructor) for instructor in self.instructors]))

        if len(self.courses) >= 1:
            d, _ = singular_or_plurial(self.courses, isMale=True)
            res += "pour %s cours %s ; " % (d, list2str([str(course) for course in self.courses]))

        if len(self.slots) >= 1:
            d, c = singular_or_plurial(self.slots, isMale=True)
            res += "pour %s slot%s %s ; " % (d, c, list2str([str(slot) for slot in self.slots]))

        if len(self.rooms) >= 1:
            d, c = singular_or_plurial(self.rooms, isMale=False)
            res += "pour %s salle%s %s ; " % (d, c, list2str([str(room) for room in self.rooms]))

        if len(self.weeks) >= 1:
            d, c = singular_or_plurial(self.weeks, isMale=False)
            res += "pour %s semaine%s %s ; " % (d, c, list2str([str(week) for week in self.weeks]))

        if len(self.days) >= 1:
            d, c = singular_or_plurial(self.days, isMale=True)
            res += "pour %s jour%s %s ; " % (d, c, list2str([str(day) for day in self.days]))

        if len(self.groups) >= 1:
            d, c = singular_or_plurial(self.groups, isMale=True)
            res += "pour %s groupe%s %s ; " % (d, c, list2str([str(group) for group in self.groups]))

        res += "doit être respectée."
        return res
