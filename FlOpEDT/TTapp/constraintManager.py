import json

from TTapp.constraint import Constraint
from TTapp.print_infaisibility import print_all

from TTapp.constraint_type import ConstraintType


def inc(occurs_types, constraint_type):
    if constraint_type is not None:
        if constraint_type in occurs_types.keys():
            occurs_types[constraint_type]["occurences"] += 1
        else:
            occurs_types[constraint_type] = {"occurences": 1}


def inc_with_type(occurs_dimension, dimension, constraint_type):
    if dimension is not []:
        for elt in dimension:
            if elt in occurs_dimension.keys():
                occurs_dimension[elt]["occurences"] += 1
                if constraint_type not in occurs_dimension[elt]["types"]:
                    occurs_dimension[elt]["types"].append(constraint_type)
            else:
                occurs_dimension[elt] = {
                    "occurences": 1,
                    "types": [constraint_type]
                }


class ConstraintManager:
    def __init__(self):
        self.threshold_type = 20 # % des types sont pris en compte
        self.threshold_attr = 80 # % des attributs sont pris en compte
        self.constraints = []
        self.infeasible_constraints = []
        self.occurs = None

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def get_nb_constraints(self):
        return len(self.constraints)

    def get_constraints(self, id_constraints):
        return [self.constraints[id_constraint] for id_constraint in id_constraints]

    def parse_iis(self, iis_filename):
        f = open(iis_filename, "r")
        data = f.read().split("Subject To\n")[1]
        constraints_declarations = data.split("Bounds")
        constraints_text = constraints_declarations[0]
        # declarations_text = constraints_declarations[1]

        constraints_text = constraints_text.split(":")
        id_constraints = [constraints_text[0]]
        for i in range(1, len(constraints_text) - 1):
            id_constraints.append(constraints_text[i].split("=")[1].split("\n")[1])
        id_constraints = list(map(lambda constraint: int(constraint[1:]), id_constraints))
        return self.get_constraints(id_constraints)

    def get_occurs(self):
        occurs = {"types": {}}
        for dimension in self.infeasible_constraints[0].dimensions.keys():
            occurs[dimension] = {}

        for constraint in self.infeasible_constraints:
            constraint_type = constraint.constraint_type.value
            inc(occurs["types"], constraint_type)
            for dimension in constraint.dimensions.keys():
                inc_with_type(occurs[dimension], constraint.dimensions[dimension]["value"], constraint_type)

        for dimension in occurs.keys():
            occurs[dimension] = {k: v for k, v in
                                 sorted(occurs[dimension].items(), key=lambda elt: elt[1]["occurences"], reverse=True)}
        return occurs

    def set_index_courses(self):
        courses = list(self.occurs["courses"].keys())

        done = []
        mat_courses = []
        for index_course in range(len(courses)):
            if index_course not in done:
                courses_equals = [courses[index_course]]
                for index_course2 in range(index_course + 1, len(courses)):
                    if courses[index_course].equals(courses[index_course2]):
                        courses_equals.append(courses[index_course2])
                        done.append(index_course2)
                if len(courses_equals) > 1:
                    mat_courses.append(courses_equals)

        for courses_equals in mat_courses:
            for index_course in range(len(courses_equals)):
                courses_equals[index_course].set_index(index_course + 1)

    def handle_reduced_result(self, ilp_file_name, weeks):
        self.infeasible_constraints = self.parse_iis(ilp_file_name)
        self.occurs = self.get_occurs()
        self.set_index_courses()
        print_brut_constraints(self.infeasible_constraints, self.occurs, weeks)
        print_factorised_constraints(self.occurs, weeks)
        print_summary_from_types(self.infeasible_constraints, self.occurs, weeks)
        print_summary_from_types_with_threshold(self.infeasible_constraints, self.occurs, weeks,
                                                self.threshold_type, self.threshold_attr)


def sort_constraints_by_type(constraints, occurs):
    order = list(occurs["types"].keys())
    constraints = sorted(constraints, key=lambda constraint: order.index(constraint.constraint_type.value))
    return constraints


def print_brut_constraints(constraints, occurs, weeks):
    constraints = sort_constraints_by_type(constraints, occurs)
    output = ""
    for constraint in constraints:
        output += str(constraint) + "\n"

    filename = "logs/intelligible_constraints2%s.txt" % weeks
    write_file(filename, output)


def print_factorised_constraints(occurs, weeks):
    output = "Sommaire des contraintes :"
    for dimension in occurs.keys():
        output += "\n\n%s:" % dimension
        for elt in occurs[dimension].keys():
            output += "\n%s -> %s" % (elt, occurs[dimension][elt]["occurences"])
            if dimension is not "types":
                output += " (%s)" % ", ".join(occurs[dimension][elt]["types"])
    filename = "logs/intelligible_constraints_factorised2%s.txt" % weeks
    write_file(filename, output)


def print_summary_from_types(constraints, occurs, weeks):
    def get_value(dictionnary, index):
        a = iter(dictionnary)
        for i in range(index - 1):
            print(next(a))
        return next(a)

    constraint = sort_constraints_by_type(constraints, occurs)[0]
    output, dimensions_to_fill = constraint.get_info_summary()

    if dimensions_to_fill is not []:
        fill = []

        for dimension_to_fill in dimensions_to_fill:
            index = 1
            if "_" in dimension_to_fill:
                s = dimension_to_fill.split("_")
                dimension_to_fill, index = s[0], int(s[1])
            for elt in occurs[dimension_to_fill]:
                if constraint.constraint_type.value not in occurs[dimension_to_fill][elt]["types"]:
                    index += 1
                else:
                    break
            fill.append(get_value(occurs[dimension_to_fill], index))
        output = output % tuple(fill)

    filename = "logs/summary_of_constraints_from_types2%s.txt" % weeks
    write_file(filename, output, print_output=False)


def get_most_important(dico, threshold, constraint_type=""):
    '''
    Retourne une liste avec les X dimensions les plus occurentes,
    dont les occurences constituent threshold % du tout.
    '''
    total = get_total_occurrences(dico, constraint_type)
    max = threshold*total/100
    current = 0
    result = []
    for key in dico.keys():
        if current >= max:
            break
        if constraint_type != "":
            if constraint_type in dico.get(key).get("types"):
                current += dico.get(key).get("occurences")
                result.append(key)
        else:
            current += dico.get(key).get("occurences")
            result.append(key)
    return result


def get_total_occurrences(dico, contraint_type):
    '''
    Retourne la somme de toutes les occurences
    '''
    total = 0
    for key in dico.keys():
        if contraint_type != "":
            if contraint_type in dico.get(key).get("types"):
                total += dico.get(key).get("occurences")
        else:
            total += dico.get(key).get("occurences")
    return total


def get_str_attr(dico, threshold, constraint_type):
    '''
    Forme une liste indenté des X attributs les plus occurents,
    dont les occurences constituent threshold % du tout.
    '''
    output = ""
    for attr in get_most_important(dico, threshold, constraint_type):
        output += "\t\t%s\n" % str(attr)
    return output


def find_object_from_type(constraint_type, constraints):
    '''
    Retourne une instance de la classe constraint correspondant au type donné,
    pour utiliser sa méthode get_summary_format().
    '''
    for constraint in constraints:
        if constraint.constraint_type.value == constraint_type:
            return constraint
    return Constraint()


def print_summary_from_types_with_threshold(constraints, occurs, weeks, threshold_type, threshold_attr):
    filename = "logs/summary_of_constraints_from_types_with_threshold%s.txt" % weeks
    output = "Voici les principaux problèmes liés à l'infaisabilité :\n"
    write_file(filename, output)
    for constraint_type in get_most_important(occurs['types'], threshold_type):
        output, dimensions = find_object_from_type(constraint_type, constraints).get_summary_format()
        fill = []
        for dimension in dimensions:
            fill.append(get_str_attr(occurs.get(dimension), threshold_attr, constraint_type))
        output %= tuple(fill)
        write_file(filename, output, mode="a+")


def write_file(filename, output, print_output=False, mode="w+"):
    if mode == 'w+':
        print("writting %s..." % filename)
    with open(filename, mode, encoding="utf-8") as file:
        file.write(output)
        file.write("\n")
    if print_output:
        print("\n%s" % output)
