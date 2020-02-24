class Constraint:
    # type = type de contrainte, par exemple "room constraint"
    def __init__(self, id, constraint_type=None, instructor=None, slot=None, course=None, week=None, room=None,
                 group=None, days=None):
        """
        if slot is not None:
            elts = str(slot).split("_"):
            # self.courseType = elts[0]
            self.days = elts[1]
            self.week = elts[2]
            # self.hour = elts[3]
        if course is not None:
            elts = str(slot).split("_"):
            # self.courseType = elts[0]
            # self.? = elts[1]
            self.instructor = elts[2]
            # self.? = elts[3]
        """
        self.id = id
        self.constraint_type = constraint_type
        self.instructor = instructor
        self.slot = slot  # a enlever
        self.course = course  # a enlever
        self.week = week
        self.room = room
        self.group = group
        self.days = days

    def get_id(self):
        return self.id

    def get_intelligible_form(self):
        res = "La contrainte %s " % self.id
        if self.constraint_type is not None:
            res += 'de type "%s" ; ' % str(self.constraint_type)
        if self.instructor is not None:
            res += "concernant le professeur %s ; " % str(self.instructor)
        if self.course is not None:
            res += "pour le cours de %s ; " % str(self.course)
        if self.slot is not None:
            res += "pour le slot %s ; " % str(self.slot)
        if self.room is not None:
            res += "dans la salle %s ; " % str(self.room)
        if self.week is not None:
            res += "pour la semaine %s ; " % str(self.week)
        if self.days is not None:
            res += "pour le jour %s ; " % str(self.days)
        if self.group is not None:
            res += "pour le groupe %s ; " % str(self.group)
        res += "ne peut pas être satisfaite"
        return res
