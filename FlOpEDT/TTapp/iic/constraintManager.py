from TTapp.iic.print_infaisibility import print_all
import csv


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
    def __init__(self, threshold_type=60, threshold_attr=80):
        self.threshold_type = threshold_type # % des types sont pris en compte
        self.threshold_attr = threshold_attr # % des attributs sont pris en compte
        self.constraints = []
        self.infeasible_constraints = []
        self.occurs = None
        self.nb_constraints = 0

    def add_constraint(self, constraint):
        self.constraints.append(constraint)
        self.nb_constraints += 1

    def get_nb_constraints(self):
        return self.nb_constraints

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

        for index_course1 in range(len(courses)):
            for index_course2 in range(index_course1 + 1, len(courses)):
                if courses[index_course1].equals(courses[index_course2]):
                    courses[index_course1].show_id = True
                    courses[index_course2].show_id = True

    def handle_reduced_result(self, ilp_file_name, department_abbrev, weeks, write_csv=False):
        self.infeasible_constraints = self.parse_iis(ilp_file_name)
        self.occurs = self.get_occurs()
        self.set_index_courses()
        print_all(self.infeasible_constraints, self.occurs, department_abbrev, weeks, self.threshold_type, self.threshold_attr)
        if write_csv:
            self.write_csv(self.infeasible_constraints, weeks)

    def write_csv(self, constraints, weeks):
        filename = "logs/weeks%s.csv" % weeks
        print("writting %s..." % filename)
        with open(filename, 'w+') as file:
            writer = csv.writer(file)
            writer.writerow(['ID', 'Constraint type', 'Instructors', 'Slots', 'Courses', 'Week', 'Rooms', 'Group',
                             'Days', 'Departement', 'Module'])
            for constraint in constraints:
                csv_info = constraint.get_csv_info()
                writer.writerow(csv_info)
