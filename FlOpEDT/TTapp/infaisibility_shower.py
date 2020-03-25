# Create result string to print
from TTapp.constraint_type import ConstraintType


def make_occur_buf(occurs):
    buf = ""
    types = ""
    for occur in occurs:
        nb_occ, types_occ = occurs.get(occur)
        n = len(types_occ)
        if n > 0:
            types = "("
            for t in range(n - 1):
                types += types_occ[t].value + ", "
            types += types_occ[n - 1].value + ")"
        buf += "[" + str(occur) + " -> " + str(nb_occ) + "] types : " + types + "\n"
    return buf


def dict2keys(dictionaries):
    res = []
    for dictionary in dictionaries:
        res.append(list(dictionary.keys()) if len(list(dictionary.keys())) >= 1 else None)
    return tuple(res)


def write_file(filename, output, print_output=False):
    print("writting %s..." % filename)
    with open(filename, "w+", encoding="utf-8") as file:
        file.write(output)
    if print_output:
        print("\n%s" % output)


def show_reduces_result_brut(constraints, occurs, weeks):
    occur_type, _, _, _, _, _, _, _, _, _ = occurs
    order = list(occur_type.keys())
    constraints = sorted(constraints, key=lambda x: order.index(x.constraint_type))
    output = ""
    for constraint in constraints:
        output += str(constraint) + "\n"
    filename = "logs/intelligible_constraints%s.txt" % weeks
    write_file(filename, output)


def show_reduces_result(occurs, weeks):
    occur_type, occur_instructor, occur_slot, occur_course, occur_week, occur_room, occur_group, occur_days, \
        occur_department, occur_modules = occurs

    buf_type = ""
    for constraint_type in occur_type:
        buf_type += "[" + constraint_type.value + " -> " + str(occur_type.get(constraint_type)) + "] \n"

    buf_instructor = make_occur_buf(occur_instructor)
    buf_slot = make_occur_buf(occur_slot)
    buf_course = make_occur_buf(occur_course)
    buf_week = make_occur_buf(occur_week)
    buf_room = make_occur_buf(occur_room)
    buf_group = make_occur_buf(occur_group)
    buf_days = make_occur_buf(occur_days)
    buf_department = make_occur_buf(occur_department)
    buf_module = make_occur_buf(occur_modules)

    output = "Sommaire des contraintes : \n"
    if buf_type != "":
        output += "\nParametre Type :\n" + buf_type
    if buf_instructor != "":
        output += "\nParametre Instructor :\n" + buf_instructor
    if buf_course != "":
        output += "\nParametre Course : \n" + buf_course
    if buf_week != "":
        output += "\nParametre Week : \n" + buf_week
    if buf_room != "":
        output += "\nParametre Room : \n" + buf_room
    if buf_group != "":
        output += "\nParametre Group : \n" + buf_group
    if buf_days != "":
        output += "\nParametre Days : \n" + buf_days
    if buf_department != "":
        output += "\nParametre Department :\n" + buf_department
    if buf_module != "":
        output += "\nParametre Module :\n" + buf_module
    if buf_slot != "":
        output += "\nParametre Slot :\n" + buf_slot
    filename = "logs/intelligible_constraints_factorised%s.txt" % weeks
    write_file(filename, output)


def show_simplified_result(occurs, weeks, max_slots_to_print=5):
    occur_type, occur_instructor, occur_slot, occur_course, occur_week, occur_room, occur_group, occur_days, \
        occur_department, occur_modules = dict2keys(occurs)

    output = "Voici les raisons principales pour lesquelles le solveur n'a pas pu résoudre l'ensemble " \
             "des contraintes spécifiées: \n"
    if occur_days is not None and occur_week is not None:
        output += "\t- Le jour %s (semaine %s) est le plus impliqué\n" % (occur_days[0], occur_week[0])

    if occur_instructor is not None:
        output += "\t- Le professeur %s est le plus impliqué\n" % occur_instructor[0]
    if occur_group is not None:
        output += "\t- Le groupe %s est le plus impliqué\n" % occur_group[0]
    if occur_modules is not None:
        output += "\t- Le module %s est le plus impliqué\n" % occur_modules[0]
    if occur_room is not None:
        output += "\t- La salle %s est la plus impliqué\n" % occur_room[0]

    if occur_slot is not None:
        output += "\n\t- Les slots les plus impliqués sont les suivants :\n"
        for i in range(min(len(occur_slot), max_slots_to_print)):
            output += "\t\t- %s\n" % occur_slot[i]

    filename = "logs/intelligible_constraints_simplified%s.txt" % weeks
    write_file(filename, output, print_output=False)


def show_result_by_type(occurs, weeks):
    occur_type, _, _, _, _, _, _, _, _, _ = dict2keys(occurs)
    if occur_type[0] == ConstraintType.DEPENDANCE:
        show_result_dependency(occurs, weeks)


def show_result_dependency(occurs, weeks):
    _, _, _, occur_courses, _, _, _, _, _, _ = dict2keys(occurs)
    output = "L'infaisabilité de l'EDT vient probablement d'un problème de dépendance entre %s et %s" \
             % (occur_courses[0], occur_courses[1])
    filename = "logs/intelligible_constraints_dependency%s.txt" % weeks
    write_file(filename, output, print_output=False)


def show_result(constraints, occurs, weeks):
    print()
    show_reduces_result_brut(constraints, occurs, weeks)
    show_reduces_result(occurs, weeks)
    show_simplified_result(occurs, weeks)
    show_result_by_type(occurs, weeks)
