from TTapp.iic.constraints.constraint import Constraint

def print_all(constraints, occurs, department_abbrev, weeks, threshold_type, threshold_attr):
    print_brut_constraints(constraints, occurs, department_abbrev, weeks)
    print_factorised_constraints(occurs, department_abbrev, weeks)
    print_summary_from_types_with_threshold(constraints, occurs, department_abbrev, weeks, threshold_type, threshold_attr)


def sort_constraints_by_type(constraints, occurs):
    order = list(occurs["types"].keys())
    constraints = sorted(constraints, key=lambda constraint: order.index(constraint.constraint_type.value))
    return constraints


def print_brut_constraints(constraints, occurs, department_abbrev, weeks):
    constraints = sort_constraints_by_type(constraints, occurs)
    output = ""
    for constraint in constraints:
        output += str(constraint) + "\n"

    filename = "logs/constraints_all_%s_%s.txt" % (department_abbrev, weeks)
    write_file(filename, output)


def print_factorised_constraints(occurs, department_abbrev, weeks):
    output = "Sommaire des contraintes :"
    for dimension in occurs.keys():
        output += "\n\n%s:" % dimension
        for elt in occurs[dimension].keys():
            output += "\n%s -> %s" % (elt, occurs[dimension][elt]["occurences"])
            if dimension != "types":
                output += " (%s)" % ", ".join(occurs[dimension][elt]["types"])
    filename = "logs/constraints_factorised_%s_%s.txt" % (department_abbrev, weeks)
    write_file(filename, output)


def get_most_important(dico, threshold, constraint_type=""):
    """
    Retourne une liste avec les X dimensions les plus occurentes,
    dont les occurences constituent threshold % du tout.
    """
    total = get_total_occurrences(dico, constraint_type)
    max_ = threshold * total / 100
    current = 0
    result = []
    for key in dico.keys():
        if current >= max_:
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
    """
    Retourne la somme de toutes les occurences
    """
    total = 0
    for key in dico.keys():
        if contraint_type != "":
            if contraint_type in dico.get(key).get("types"):
                total += dico.get(key).get("occurences")
        else:
            total += dico.get(key).get("occurences")
    return total


def get_str_attr(dico, threshold, constraint_type):
    """
    Forme une liste indenté des X attributs les plus occurents,
    dont les occurences constituent threshold % du tout.
    """
    output = ""
    for attr in get_most_important(dico, threshold, constraint_type):
        output += "\t\t%s\n" % str(attr)
    return output


def find_object_from_type(constraint_type, constraints):
    """
    Retourne une instance de la classe constraint correspondant au type donné,
    pour utiliser sa méthode get_summary_format().
    """
    for constraint in constraints:
        if constraint.constraint_type.value == constraint_type:
            return constraint
    return Constraint()


def print_summary_from_types_with_threshold(constraints, occurs, department_abbrev, weeks,
                                            threshold_type, threshold_attr, print_output=True):
    filename = "logs/constraints_summary_%s_%s.txt" % (department_abbrev, weeks)
    output = "Voici les principaux problèmes liés à l'infaisabilité :\n"
    print(output)
    write_file(filename, output)
    for constraint_type in get_most_important(occurs['types'], threshold_type):
        output, dimensions = find_object_from_type(constraint_type, constraints).get_summary_format()
        fill = []
        for dimension in dimensions:
            fill.append(get_str_attr(occurs.get(dimension), threshold_attr, constraint_type))
        output %= tuple(fill)
        write_file(filename, output, mode="a+", print_output=print_output)


def write_file(filename, output, print_output=False, mode="w+"):
    if mode == 'w+':
        print("writting %s..." % filename)
    with open(filename, mode, encoding="utf-8") as file:
        file.write(output)
        file.write("\n")
    if print_output:
        print("\n%s" % output)
