from base.models import Course, TrainingProgramme, Group, Department
from configuration.deploy_database import extract_database_file
from MyFlOp.database_ENSMM import database_ENSMM
from MyFlOp.cours_ENSMM import cours_ENSMM
from configuration.hyperplanning import extract_courses_from_book
from misc.assign_colors import assign_module_color


def global_extraction(abbrev='ENSMM', name='ENSMM', delete_groups=False):
    extract_database_file(abbrev, name, database_ENSMM)
    dep = Department.objects.get(abbrev=abbrev)
    extract_courses_from_book(cours_ENSMM, dep, assign_colors=False)
    apply_group_architecture(find_group_architecture(dep))
    if delete_groups:
        g, tp = useless_groups_and_train_progs(dep)
        delete_useless_groups(g, tp)
    assign_module_color(dep)


def find_group_architecture(dep):
    result = {}
    for tp in TrainingProgramme.objects.filter(department=dep):
        result[tp.name]={}
        G = Group.objects.filter(train_prog=tp)
        for g in G:
            result[tp.name][g.name] = set()
            for g2 in G.exclude(id=g.id):
                if g2.name.startswith(g.name):
                    result[tp.name][g.name].add(g2.name)
            if not result[tp.name][g.name]:
                result[tp.name].pop(g.name)
        if not result[tp.name]:
            result.pop(tp.name)
    return result


def apply_group_architecture(group_architecture_dict):
    d = group_architecture_dict
    for tp in d:
        tpg = Group.objects.get(train_prog__name=tp, name=tp)
        for g in d[tp]:
            G = Group.objects.get(train_prog__name=tp, name=g)
            for g2 in d[tp][g]:
                G2 = Group.objects.get(train_prog__name=tp, name=g2)
                for pg in G2.parent_groups.all():
                    G2.parent_groups.remove(pg)
                G2.parent_groups.add(G)


def useless_groups_and_train_progs(dep):
    groups = set()
    train_progs = set()
    G = Group.objects.filter(train_prog__department=dep)
    C = Course.objects.filter(type__department=dep)
    for g in G:
        cg = C.filter(groups__in={g} | g.descendants_groups())
        if not cg:
            groups.add(g)
    for tp in TrainingProgramme.objects.filter(department=dep):
        if all(g in groups for g in G.filter(train_prog=tp)):
            train_progs.add(tp)
    return groups, train_progs


def delete_useless_groups(useless_groups, useless_train_progs):
    for g in useless_groups:
        g.delete()
    for tp in useless_train_progs:
        tp.delete()
