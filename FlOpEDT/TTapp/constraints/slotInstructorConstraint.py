from TTapp.constraint import Constraint


class SlotInstructorConstraint(Constraint):
    def __init__(self, slot, instructor):
        self.slot = slot
        self.instructor = instructor
        Constraint.__init__(self, constraint_type=ConstraintType.PAS_DE_PROFESSEUR_DISPONIBLE, slots=[slot], instructors=[instructor])

    def get_info_summary(self):
        output = "Le professeur %s n'est pas disponible le %"
        dimensions_to_fill = ["instructors", "slots"]
        return output, dimensions_to_fill
