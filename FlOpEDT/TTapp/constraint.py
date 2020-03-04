def singular_or_plurial(my_list, is_male):
    determinant = "les" if len(my_list) > 1 else ("le" if is_male else "la")
    conjugation = "s" if len(my_list) > 1 else ""
    return determinant, conjugation


def list2str(my_list):
    if len(my_list) == 1:
        return my_list[0]

    output = "["
    for i in range(len(my_list) - 1):
        output += my_list[i] + ", "
    return output + my_list[-1] + "]"


class Constraint:
    def __init__(self, id, constraint_type=None, instructors=[], slots=[], courses=[], weeks=[], rooms=[],
                 groups=[], days=[], departments=[]):
        self.id = id
        self.constraint_type = constraint_type

        if type(instructors) is not list:
            instructors = [instructors]
        self.instructors = list(instructors)

        if type(weeks) is not list:
            weeks = [weeks]
        self.weeks = list(weeks)

        if type(rooms) is not list:
            rooms = [rooms]
        self.rooms = list(rooms)

        if type(groups) is not list:
            groups = [groups]
        self.groups = list(groups)

        if type(days) is not list:
            days = [days]
        self.days = list(days)

        if type(departments) is not list:
            departments = [departments]
        self.departments = list(departments)

        if type(slots) is not list:
            slots = [slots]
        self.slots = list(slots)

        if type(courses) is not list:
            courses = [courses]
        self.courses = list(courses)

        for s in self.slots:
            self.days.append(s.get_day().day)
            self.weeks.append(s.get_day().week)

        self.modules = []
        for c in self.courses:
            self.instructors.append(c.get_tutor())
            self.groups.append(c.get_group())
            self.modules.append(c.get_module())
        #self.courses = list(self.modules)

    def get_id(self):
        return self.id

    def __str__(self):
        res = "(%s) La contrainte " % self.id
        if self.constraint_type is not None:
            res += 'de type "%s" ; ' % str(self.constraint_type)

        if len(self.instructors) >= 1:
            d, c = singular_or_plurial(self.instructors, is_male=True)
            res += "pour %s professeur%s %s ; " % (d, c, list2str([str(instructor) for instructor in self.instructors]))

        if len(self.courses) >= 1:
            d, _ = singular_or_plurial(self.courses, is_male=True)
            res += "pour %s cours %s ; " % (d, list2str([str(course) for course in self.courses]))

        if len(self.slots) >= 1:
            d, c = singular_or_plurial(self.slots, is_male=True)
            res += "pour %s slot%s %s ; " % (d, c, list2str([str(slot) for slot in self.slots]))

        if len(self.rooms) >= 1:
            d, c = singular_or_plurial(self.rooms, is_male=False)
            res += "pour %s salle%s %s ; " % (d, c, list2str([str(room) for room in self.rooms]))

        if len(self.weeks) >= 1:
            d, c = singular_or_plurial(self.weeks, is_male=False)
            res += "pour %s semaine%s %s ; " % (d, c, list2str([str(week) for week in self.weeks]))

        if len(self.groups) >= 1:
            d, c = singular_or_plurial(self.groups, is_male=True)
            res += "pour %s groupe%s %s ; " % (d, c, list2str([str(group) for group in self.groups]))

        if len(self.days) >= 1:
            d, c = singular_or_plurial(self.days, is_male=True)
            res += "pour %s jour%s %s ; " % (d, c, list2str([str(day) for day in self.days]))

        if len(self.departments) >= 1:
            d, c = singular_or_plurial(self.departments, is_male=True)
            res += "pour %s departement%s %s ; " % (d, c, list2str(
                [str(department) for department in self.departments]))

        res += "doit être respectée."
        return res
