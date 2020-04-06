import json
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
            index = 0
            if "_" in dimension_to_fill:
                s = dimension_to_fill.split("_")
                dimension_to_fill, index = s[0], int(s[1])
            fill.append(get_value(occurs[dimension_to_fill], index))

        output = output % tuple(fill)

    filename = "logs/summary_of_constraints_from_types2%s.txt" % weeks
    write_file(filename, output, print_output=False)


def write_file(filename, output, print_output=False):
    print("writting %s..." % filename)
    with open(filename, "w+", encoding="utf-8") as file:
        file.write(output)
        file.write("\n")
    if print_output:
        print("\n%s" % output)
