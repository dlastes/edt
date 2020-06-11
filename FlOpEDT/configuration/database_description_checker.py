#
# This code finds the list of problems in a description of a database,
# for example the result of parse_file in parse_database_file_xlsx.py.
#
# The goal is that if there's any problem with what the user entered,
# it is seen, it is precisely diagnosed and explained : no need to ask.
#
# Each problem should be a string describing the problem. It should
# start with "D:" if it's a developer problem, otherwise it should be
# a very direct and explicit indication of what was wrong.
#
# The checks go from the very basic (structural, typing) to the more
# specific, in turn.
#
# The basic organisation of the file is the following :
# - helper functions for first level checkers
# - first level checkers
# - <helpers and checkers of higher levels>
# - main checker
#

##########################################
#                                        #
#          Helper functions              #
#                                        #
##########################################

def check_identifiers(ids, name):
    result = []
    found_issue1 = False
    found_issue2 = False
    found_issue3 = False
    for id_ in ids:
        if not found_issue1 and id_ == None:
            result.append(f"D: (at least) one of the {name} has a None identifier!")
            found_issue1 = True
        elif not found_issue2 and not isinstance(id_, str):
            result.append(f"D: (at least) one of the {name} has a non-string identifier!")
            found_issue2 = True
        elif not found_issue3 and id_ == '':
            result.append(f"D: (at least) one of the {name} has an empty identifier!")
            found_issue3 = True
    return result

def check_type(obj, type_, name):
    result = []
    if not isinstance(obj, type_):
        result.append(f"D: {name} isn't a '{type_.__name__}'")
    return result

##########################################
#                                        #
#       Individual chunk checks          #
#                                        #
##########################################

def check_rooms(rooms):
    result = []
    if not isinstance(rooms, set):
        result.append("D: the rooms chunk should be a 'set'")
    else:
        result.extend(check_identifiers(rooms, "rooms"))
    return result

def check_room_groups(room_groups):
    result = []
    if not isinstance(room_groups, dict):
        result.append("D: the room_groups chunk should be a 'dict'")
    else:
        result.extend(check_identifiers(room_groups.keys(), "room groups"))
    return result

def check_room_categories(room_categories):
    result = []
    if not isinstance(room_categories, dict):
        result.append("D: the room categories chunk should be a 'dict'")
    else:
        result.extend(check_identifiers(room_categories.keys(), "room categories"))
    return result

def check_people(people):
    result = []
    if not isinstance(people, dict):
        result.append("D: the people chunk should be a 'dict'")
        return result
    result.extend(check_identifiers(people.keys(), "people"))
    if len(result) > 0:
        return result
    for id_, person in people.items():
        if not isinstance(person, dict):
            result.append(f"D: person '{id_}' should be a 'dict'")
            continue
        if person.keys() != { 'first_name', 'last_name', 'email', 'status', 'employer' }:
            result.append(f"D: person '{id_}' doesn't have the expected keys")
            continue
        if person['status'] not in ['Vacataire', 'Permanent']:
            result.append(f"D: person '{id_}' doesn't have a correct status")
            continue
    return result

def check_modules(modules):
    result = []
    if not isinstance(modules, dict):
        result.append("D: the modules chunk should be a 'dict'")
        return result
    result.extend(check_identifiers(modules.keys(), "module"))
    if len(result) > 0:
        return result
    for id_, module in modules.items():
        if not isinstance(module, dict):
            result.append("D: module '{id_}' should be a 'dict'")
            continue
        if module.keys() != { 'PPN', 'name', 'promotion', 'period', 'responsable' }:
            result.append(f"D: module '{id_}' doesn't have the expected keys")
            continue
        for key, val in module.items():
            result.extend(check_type(val, str, f"field '{key}' of module '{id_}'"))
    return result

def check_cours(cours):
    result = []
    if not isinstance(cours, dict):
        result.append("D: the cours chunk should be a 'dict'")
        return result
    result.extend(check_identifiers(cours.keys(), "cours"))
    if len(result) > 0:
        return result
    for id_, elem in cours.items():
        if not isinstance(elem, dict):
            result.append("D: cours '{id_}' should be a 'dict'")
            continue
        if elem.keys() != { 'duration', 'group_types', 'start_times' }:
            result.append(f"D: cours '{id_}' doesn't have the expected keys")
            continue
        result.extend(check_type(elem['duration'], int, f"duration of cours '{id_}'"))
        if isinstance(elem['group_types'], set):
            result.extend(check_identifiers(elem['group_types'],
                                            f"group types of cours {id_}"))
        else:
            result.append(f"D: group types of cours '{id_}' isn't a set")
        if isinstance(elem['start_times'], set):
            for time in elem['start_times']:
                result.extend(check_type(time, int, f"one of the start times of cours '{id_}'"))
        else:
            result.append(f"D: start times of cours '{id_}' isn't a 'set'")
    return result

def check_settings(settings):
    result = []
    if not isinstance(settings, dict):
        result.append("D: the settings chunk should be a 'dict'")
        return result
    if settings.keys() != { 'day_start_time', 'day_finish_time',
                            'lunch_break_start_time', 'lunch_break_finish_time',
                            'default_preference_duration', 'days', 'periods'}:
        result.append(f"D: settings doesn't have the expected keys")
        return result

    result.extend(check_type(settings['day_start_time'], int, "Day start time in settings"))
    result.extend(check_type(settings['day_finish_time'], int, "Day finish time in settings"))
    result.extend(check_type(settings['lunch_break_start_time'], int, "Lunch break start time in settings"))
    result.extend(check_type(settings['lunch_break_finish_time'], int, "Lunch break finish time in settings"))
    result.extend(check_type(settings['default_preference_duration'], int, "Default preference duration in settings"))
    if isinstance(settings['days'], list):
        if not set(settings['days']).issubset({'m', 'tu', 'w', 'th', 'f', 'sa', 'su'}):
            result.append("D: the days in settings contain invalid values")
    else:
        result.append("D: the days in settings should be a 'set'")

    if isinstance(settings['periods'], dict):
        for id_, val in settings['periods'].items():
            if isinstance(val, tuple) and len(val) == 2:
                result.extend(check_type(val[0], int, f"start week for period '{id_}' in settings"))
                result.extend(check_type(val[1], int, f"finish week for period '{id_}' in settings"))
            else:
                result.append(f"D: the data for period '{id_}' in settings should be a pair")
    else:
        result.append("D: the periods in settings should be a 'dict'")

    return result

def check_promotions(promotions):
    result = []
    if not isinstance(promotions, dict):
        result.append("D: the promotions chunk should be a 'dict'")
        return result
    result.extend(check_identifiers(promotions.keys(), "promotions"))
    for id_, name in promotions.items():
        result.extend(check_type(name, str, f"name of promotion '{id_}'"))
    return result

def check_group_types(group_types):
    result = []
    if not isinstance(group_types, set):
        result.append("D: the group types chunk should be a 'set'")
        return result
    result.extend(check_identifiers(group_types, "group types"))
    return result

def check_groups(groups):
    result = []
    if not isinstance(groups, dict):
        result.append("D: the groups chunk should be a 'dict'")
        return result
    result.extend(check_identifiers(groups.keys(), "groups"))
    for id_, group in groups.items():
        if isinstance(group, dict):
            if group.keys() != { 'promotion', 'group_type', 'parent'}:
                result.append(f"D: group '{id_}' doesn't have the expected keys")
            else:
                result.extend(check_type(group['promotion'], str, f"promotion of group '{id_}'"))
                result.extend(check_type(group['group_type'], str, f"group type of group '{id_}'"))
                if isinstance(group['parent'], set):
                    if len(group['parent']) > 1:
                        result.append(f"D: group '{id_}' should have at most one parent")
                    elif len(group['parent']) == 1:
                        for parent in group['parent']: # how does one peek in a set?
                            result.extend(check_type(parent, str, f"parent of group '{id_}'"))
                else:
                    result.append(f"D: the parent of group '{id_}' isn't a set")
        else:
            result.append(f"Group '{id_}' isn't a 'dict'")
    return result

##########################################
#                                        #
#            Cross checks                #
#                                        #
##########################################

# BIG FIXME! THAT'S WHERE THE USER GETS EXPLAINED WHAT WAS DONE WRONG!

##########################################
#                                        #
#        Main checker function           #
#                                        #
##########################################

def database_description_check (database):
    result = []

    if not isinstance(database, dict):
        result.append("D: the database description isn't even a dictionary!")
        return result

    separate_checkers = {
        'rooms': check_rooms,
        'room_groups': check_room_groups,
        'room_categories': check_room_categories,
        'people': check_people,
        'modules': check_modules,
        'cours': check_cours,
        'settings': check_settings,
        'promotions': check_promotions,
        'group_types': check_group_types,
        'groups': check_groups
    }

    invalid_keys = set(database.keys())
    invalid_keys.difference_update(separate_checkers.keys())
    if len(invalid_keys) > 0:
        result.append("D: the database description has invalid keys: {0:s}".format(', '.join(invalid_keys)))
        return result

    missing_keys = set(separate_checkers.keys())
    missing_keys.difference_update(database.keys())
    if len(missing_keys) > 0:
        result.append("D: the database description misses some keys: {0:s}".format(', '.join(invalid_keys)))
        return result

    for key, checker in separate_checkers.items():
        result.extend(checker(database[key]))

    # stop here, so the next tests can depend on a small amount of sanity
    if len(result) > 0:
        return result

    # BIG FIXME: here comes the second round - user-oriented, this time

    return result


if __name__ == '__main__':
    from parse_database_file_xlsx import parse_file
    print("=========== PARSING BEGIN ============")
    database = parse_file()
    print("=========== PARSING END ============")
    print("Remarks:")
    remarks = database_description_check(database)
    if len(remarks) == 0:
        print(" nil")
    else:
        for remark in remarks:
            print(remark)
