from TTapp.iic.constraints.constraint import Constraint
from TTapp.iic.constraint_type import ConstraintType

class SlotInstructorConstraint(Constraint):
    def __init__(self, slot, instructor):
        self.slot = slot
        self.instructor = instructor
        Constraint.__init__(self, constraint_type=ConstraintType.PAS_DE_PROFESSEUR_DISPONIBLE, slots=[slot], instructors=[instructor])

    def get_summary_format(self):
        output = "\tLe professeur \n%s n'est pas disponible le slot : \n%s"
        dimensions = ["instructors", "slots"]
        return output, dimensions
