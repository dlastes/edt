from TTapp.constraint import Constraint


class SimulSlotGroupConstraint(Constraint):
    def __init__(self, slot, group):
        self.slot = slot
        self.group = group
        Constraint.__init__(self, constraint_type=ConstraintType.PAS_PLUS_1_COURS_PAR_CRENEAU, slots=[slot], groups=[group])

    def get_info_summary(self):
        output = "Trop de cours simultanés pour le slot %s et le groupe %s"
        dimensions_to_fill = ["slots", "groups"]
        return output, dimensions_to_fill
