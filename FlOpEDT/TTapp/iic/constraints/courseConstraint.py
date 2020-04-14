from TTapp.iic.constraints.constraint import Constraint
from TTapp.iic.constraint_type import ConstraintType

class CourseConstraint(Constraint):
    def __init__(self, course):
        self.course = course
        Constraint.__init__(self, constraint_type=ConstraintType.COURS_DOIT_ETRE_PLACE,
                            courses=[course])

    def get_summary_format(self):
        output = "\tLe cours \n%s doit être placé\n"
        dimensions = ["courses"]
        return output, dimensions
