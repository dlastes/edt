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


def dict_to_keys(dictionaries):
    res = []
    for dictionary in dictionaries:
        res.append(list(dictionary.keys()) if len(list(dictionary.keys())) >= 1 else None)
    return tuple(res)


def write_file(filename, output, print_output=False, mode="w+"):
    if(mode == 'w+'):
        print("writting %s..." % filename)
    with open(filename, mode, encoding="utf-8") as file:
        file.write(output)
        file.write("\n")
    if print_output:
        print("\n%s" % output)


def print_brut_constraints(constraints, occurs, weeks):
    occur_type, _, _, _, _, _, _, _, _, _ = occurs
    order = list(occur_type.keys())
    constraints = sorted(constraints, key=lambda x: order.index(x.constraint_type))
    output = ""
    for constraint in constraints:
        output += str(constraint) + "\n"
    filename = "logs/intelligible_constraints%s.txt" % weeks
    write_file(filename, output)


def print_occurrence_of_constraints(occurs, weeks):
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

    output = "Sommaire des contraintes :\n"
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


def print_summary_of_constraints(occurs, weeks, max_slots_to_print=5):
    occur_type, occur_instructor, occur_slot, occur_course, occur_week, occur_room, occur_group, occur_days, \
        occur_department, occur_modules = dict_to_keys(occurs)

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


def print_summary_from_type(occurs, weeks):
    threshold_type = 90 # % des types sont pris en compte
    threshold_attr = 90 # % des attributs sont pris en compte

    occur_type = occurs[0]
    keys = list(occur_type.keys())

    filename = "logs/summary_of_constraints_from_types%s.txt" % weeks
    output = "Voici les principaux problèmes liés à l'infaisabilité :\n"
    write_file(filename, output)

    for i in range(number_of_important_types(occur_type, threshold_type)):
        type = keys[i]

        if type == ConstraintType.DEPENDANCE:
            print_summary_dependency(occurs, filename, threshold_attr)

        elif type == ConstraintType.COURS_DOIT_AVOIR_PROFESSEUR:
            print_summary_cours_prof(occurs, filename, threshold_attr)

        elif type == ConstraintType.PAS_DE_PROFESSEUR_DISPONIBLE:
            print_summary_pas_de_prof(occurs, filename, threshold_attr)

        elif False:
            pass # TODO


def print_summary_dependency(occurs, filename, threshold):
    courses = occurs[3]
    output = "\tProblème de dépendance entre les cours suivants:\n"
    output += get_str_attr(courses, threshold, ConstraintType.DEPENDANCE)
    write_file(filename, output, mode="a+")


def print_summary_cours_prof(occurs, filename, threshold):
    courses = occurs[3]
    prof = occurs[1]
    output = "\tLes cours suivants:\n"
    output += get_str_attr(courses, threshold, ConstraintType.COURS_DOIT_AVOIR_PROFESSEUR)
    output += "\tdevraient avoir un professeur, surement parmis:\n"
    output += get_str_attr(prof, threshold, ConstraintType.COURS_DOIT_AVOIR_PROFESSEUR)
    write_file(filename, output, mode="a+")


def print_summary_pas_de_prof(occurs, filename, threshold):
    prof = occurs[1]
    output = "\tLes professeurs suivants:\n"
    output += get_str_attr(prof, threshold, ConstraintType.PAS_DE_PROFESSEUR_DISPONIBLE)
    output += "\tdevraient pouvoir faire cours\n"
    write_file(filename, output, mode="a+")


def get_str_attr(attr_tab, threshold, type):
    output = ""
    for attr in get_important_attr(attr_tab, threshold, type):
        output += "\t\t%s\n" % str(attr)
    return output


def number_of_important_types(occur_type, threshold):
    total = get_total_occurrences_type(occur_type)
    max = threshold*total/100
    current = 0
    count = 0
    for type in occur_type:
        if current >= max:
            break
        current += occur_type.get(type)
        count += 1
    return count


def get_total_occurrences_type(occur_type):
    total = 0
    for type in occur_type:
        total += occur_type.get(type)
    return total


def get_important_attr(occur_attr, threshold, type):
    total = get_total_occurrences_attr(occur_attr, type)
    max = threshold*total/100
    current = 0
    tab = []
    for attr in occur_attr:
        if current >= max:
            break
        if type in occur_attr.get(attr)[1]:
            current += occur_attr.get(attr)[0]
            tab.append(attr)
    return tab


def get_total_occurrences_attr(occur_attr, type):
    total = 0
    for attr in occur_attr:
        if type in occur_attr.get(attr)[1]:
            total += occur_attr.get(attr)[0]
    return total


def print_all(constraints, occurs, weeks):
    print_brut_constraints(constraints, occurs, weeks)
    print_occurrence_of_constraints(occurs, weeks)
    print_summary_of_constraints(occurs, weeks)
    print_summary_from_type(occurs, weeks)


#===================================================================================


def test_run():
    test_get_total_occurrences_type()
    test_number_of_important_types()
    test_get_total_occurrences_attr()
    test_get_important_attr()

def test_get_total_occurrences_type():
    dico = {}
    dico["type1"] = 3
    dico["type2"] = 4
    print("test_get_total_occurrences_type : " + str(get_total_occurrences_type(dico) == 7))


def test_number_of_important_types():
    dico = {}
    dico["1"] = 84
    dico["2"] = 45
    dico["3"] = 24
    dico["4"] = 2
    dico["5"] = 2
    dico["6"] = 1
    print("test_number_of_important_types : " + str(number_of_important_types(dico, 75) == 2))


def test_get_total_occurrences_attr():
    dico = {}
    dico["attr1"] = (3, [ConstraintType.IBD_EQ])
    dico["attr2"] = (4, [ConstraintType.DEPENDANCE]) ##
    dico["attr3"] = (3, [ConstraintType.DEPENDANCE, ConstraintType.IBD_EQ]) ##
    print("test_get_total_occurrences_attr : " + str(get_total_occurrences_attr(dico, ConstraintType.DEPENDANCE) == 7))


def test_get_important_attr():
    dico = {}
    dico["1"] = (384, [ConstraintType.IBD_EQ])
    dico["2"] = (45, [ConstraintType.DEPENDANCE]) ##
    dico["3"] = (24, [ConstraintType.DEPARTEMENT_BLOQUE_SLOT, ConstraintType.AVOID_BOTH_TIME, ConstraintType.DEPENDANCE]) ##
    dico["4"] = (2, [ConstraintType.DEPENDANCE, ConstraintType.CONJONCTION]) ##
    dico["5"] = (2, [])
    dico["6"] = (1, [ConstraintType.DEPENDANCE]) ##
    print("test_get_important_attr : " + str(get_important_attr(dico, 75, ConstraintType.DEPENDANCE) == ['2', '3']))


def test_print_summary_from_type():
    dico = {}
    dico[ConstraintType.DEPENDANCE] = 200
    dico[ConstraintType.CONJONCTION] = 25
    dico[ConstraintType.AVOID_BOTH_TIME] = 25
    dico[ConstraintType.CDU_VEUT_VENIR_1_JOUR_ENTIER_QUAND_6_CRENEAUX] = 25
    dico[ConstraintType.IBD_EQ] = 25
    dico[ConstraintType.B219_TO_LP] = 25
    cours = {}
    cours["cours1"] = (200, [ConstraintType.CONJONCTION, ConstraintType.AVOID_BOTH_TIME])
    cours["cours2"] = (10, [ConstraintType.DEPENDANCE, ConstraintType.AVOID_BOTH_TIME])
    cours["cours3"] = (4, [ConstraintType.DEPARTEMENT_BLOQUE_SLOT, ConstraintType.DEPENDANCE])
    dicos_tab = [dico, "", "", cours, "", "", "", "", "", ""]
    print_summary_from_type(dicos_tab, [1])
