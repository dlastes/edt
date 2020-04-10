from TTapp.constraint import Constraint


class CourseConstraint(Constraint):
    def __init__(self, course):
        self.course = course
        Constraint.__init__(self, constraint_type=ConstraintType.COURS_DOIT_ETRE_PLACE,
                            courses=[course])

    def get_info_summary(self):
        output = "Le cours %s doit être placé"
        dimensions_to_fill = ["course"]
        return output, dimensions_to_fill
