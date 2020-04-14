from TTapp.iic.constraints.constraint import Constraint


class InstructorConstraint(Constraint):
    def __init__(self, constraint_type, slot, course):
        self.slot = slot
        self.course = course
        Constraint.__init__(self, constraint_type=constraint_type, courses=[course], slots=[slot])

    def get_summary_format(self):
        output = "\tLes cours suivants:\n%s\tdoivent avoir un professeur\n"
        dimensions = ["courses"]
        return output, dimensions
