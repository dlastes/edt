from TTapp.constraint import Constraint


class InstructorConstraint(Constraint):
    def __init__(self, constraint_type, slot, course):
        self.slot = slot
        self.course = course
        Constraint.__init__(self, constraint_type=constraint_type, courses=[course], slots=[slot])

    def get_info_summary(self):
        output = "Le cours %s doit avoir un professeur"
        dimensions_to_fill = ["courses"]
        return output, dimensions_to_fill

    def get_summary_format(self):
        output = "\tLes cours suivants:\n%s\tdoivent avoir un professeur, surement parmis:\n%s"
        dimensions = ["courses", "instructors"]
        return output, dimensions