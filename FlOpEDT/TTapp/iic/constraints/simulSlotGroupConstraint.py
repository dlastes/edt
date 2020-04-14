from TTapp.iic.constraints.constraint import Constraint
from TTapp.iic.constraint_type import ConstraintType

class SimulSlotGroupConstraint(Constraint):
    def __init__(self, slot, group):
        self.slot = slot
        self.group = group
        Constraint.__init__(self, constraint_type=ConstraintType.PAS_PLUS_1_COURS_PAR_CRENEAU, slots=[slot], groups=[group])

    def get_summary_format(self):
        output = "\tTrop de cours simultanés pour le slot : \n%s et le groupe : \n%s"
        dimensions = ["slots", "groups"]
        return output, dimensions
