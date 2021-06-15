from TTapp.TTConstraint import max_weight
from base.models import TrainingProgramme
from TTapp.slots import slots_filter, days_filter
from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.ilp_constraints.constraint import Constraint


def add_ensmm_specific_constraints(ttmodel):

    # LV Groups are transversals
    for tp in ttmodel.train_prog:
        transversal_groups = ttmodel.wdb.groups.filter(train_prog=tp, name__contains='LV')
        n_tg = transversal_groups.count()
        if n_tg == 0:
            continue
        for bg in ttmodel.wdb.basic_groups.filter(train_prog=tp).exclude(name__contains='LV'):
            for sl1 in ttmodel.wdb.courses_slots:
                for sl2 in slots_filter(ttmodel.wdb.courses_slots, simultaneous_to=sl1):
                    ttmodel.add_constraint(ttmodel.sum(ttmodel.TT[(sl1, c1)]
                                                       for g1 in transversal_groups
                                                       for c1 in ttmodel.wdb.courses_for_group[g1]
                                                       & ttmodel.wdb.compatible_courses[sl1]) * 1/n_tg +
                                           ttmodel.sum(ttmodel.TT[(sl2, c2)]
                                                       for c2 in ttmodel.wdb.courses_for_basic_group[bg]
                                                       & ttmodel.wdb.compatible_courses[sl2]),
                                           '<=', 1,
                                           Constraint(constraint_type=ConstraintType.SIMUL_SLOT,
                                                      groups=bg, slots=[sl1, sl2])
                                           )
