from TTapp.print_infaisibility import print_all


def parse_iis(iis_filename):
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
    return id_constraints


def inc(dic, key):
    if key is not None:
        if key in dic.keys():
            dic[key] += 1
        else:
            dic[key] = 1


# To link the type of the constraint to the parameter occurence
def inc_with_type(dic, keys, c_type):
    if keys is not []:
        for key in keys:
            if key in dic.keys():
                dic[key][0] += 1
                if dic[key][1].count(c_type) == 0:
                    dic[key][1].append(c_type)
            else:
                dic[key] = [1, [c_type]]


def handle_occur_type_with_priority(priority_types, occur_type, decreasing):
    if priority_types is []:
        return occur_type
    nb_occ_init = []
    max_priority = max(occur_type.values()) + len(priority_types)
    min_priority = -len(priority_types) + 1
    for priority_type in priority_types:
        if priority_type in occur_type:
            nb_occ_init.append(occur_type[priority_type])
            occur_type[priority_type] = max_priority if decreasing else min_priority
            max_priority -= 1
            min_priority += 1
    occur_type = {k: v for k, v in sorted(occur_type.items(), key=lambda item: item[1], reverse=decreasing)}
    for i in range(len(priority_types)):
        if priority_types[i] in occur_type:
            occur_type[priority_types[i]] = nb_occ_init[i]
    return occur_type


def get_occurs(constraints, decreasing=True):
    occur_type = {}
    occur_instructor = {}
    occur_slot = {}
    occur_course = {}
    occur_week = {}
    occur_room = {}
    occur_group = {}
    occur_days = {}
    occur_departments = {}
    occur_module = {}

    # Initiate all occurences
    for constraint in constraints:
        c_type = constraint.constraint_type
        inc(occur_type, constraint.constraint_type)
        inc_with_type(occur_instructor, constraint.instructors, c_type)
        inc_with_type(occur_slot, constraint.slots, c_type)
        inc_with_type(occur_course, constraint.courses, c_type)
        inc_with_type(occur_week, constraint.weeks, c_type)
        inc_with_type(occur_room, constraint.rooms, c_type)
        inc_with_type(occur_group, constraint.groups, c_type)
        inc_with_type(occur_days, constraint.days, c_type)
        inc_with_type(occur_departments, constraint.departments, c_type)
        inc_with_type(occur_module, constraint.modules, c_type)

    priority_types = []
    occur_type = handle_occur_type_with_priority(priority_types, occur_type, decreasing)

    occur_instructor = {k: v for k, v in
                        sorted(occur_instructor.items(), key=lambda item: item[1][0], reverse=decreasing)}
    occur_slot = {k: v for k, v in sorted(occur_slot.items(), key=lambda item: item[1][0], reverse=decreasing)}
    occur_course = {k: v for k, v in sorted(occur_course.items(), key=lambda item: item[1][0], reverse=decreasing)}
    occur_week = {k: v for k, v in sorted(occur_week.items(), key=lambda item: item[1][0], reverse=decreasing)}
    occur_room = {k: v for k, v in sorted(occur_room.items(), key=lambda item: item[1][0], reverse=decreasing)}
    occur_group = {k: v for k, v in sorted(occur_group.items(), key=lambda item: item[1][0], reverse=decreasing)}
    occur_days = {k: v for k, v in sorted(occur_days.items(), key=lambda item: item[1][0], reverse=decreasing)}
    occur_departments = \
        {k: v for k, v in sorted(occur_departments.items(), key=lambda item: item[1][0], reverse=decreasing)}
    occur_module = {k: v for k, v in sorted(occur_module.items(), key=lambda item: item[1][0], reverse=decreasing)}

    return occur_type, occur_instructor, occur_slot, occur_course, occur_week, occur_room, occur_group, \
           occur_days, occur_departments, occur_module


def set_index_courses(occurs):
    _, _, _, occur_course, _, _, _, _, _, _ = occurs
    courses = list(occur_course.keys())

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


class ConstraintManager:
    def __init__(self):
        self.constraints = []

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def get_constraint_by_id(self, id_constraint):
        return self.constraints[id_constraint]

    def get_constraints_by_ids(self, id_constraints):
        return [self.constraints[id_constraint] for id_constraint in id_constraints]

    def handle_reduced_result(self, ilp_file_name, weeks):
        id_constraints = parse_iis(ilp_file_name)
        constraints = self.get_constraints_by_ids(id_constraints)
        occurs = get_occurs(constraints)
        set_index_courses(occurs)
        print_all(constraints, occurs, weeks)
        self.write_csv(constraints, weeks)

    def write_csv(self, constraints, weeks):
        import csv
        with open("weeks%s.csv" % weeks, 'w') as file:
            writer = csv.writer(file)
            writer.writerow(['ID', 'Constraint type', 'Instructors', 'Slots', 'Courses', 'Week', 'Rooms', 'Group', 'Days', 'Departement', 'Module'])
            for constraint in constraints:
                csv_info = constraint.get_csv_info()
                writer.writerow(csv_info)
