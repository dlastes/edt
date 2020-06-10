from openpyxl import load_workbook

import logging
logger = logging.getLogger(__name__)

people_sheet = 'Intervenants'
rooms_sheet = 'Salles'
REASONABLE = 3141 # large enough?

def string_cell(sheet, row, column):
    "Helper function to get a clean string out of a cell"
    "(will return '' if there's nothing to see)"

    val = sheet.cell(row=row, column=column).value
    if val == None:
        return ''
    val = str(val).strip()
    return val

def find_cell(sheet, marker):
    "Helper function to find the marker of a data block"
    "(Will return either row, col or None, None)"

    row, col = 1, 1
    while row < REASONABLE:
        while col < REASONABLE:
            if string_cell(sheet, row, col) == marker:
                return row, col
            col = col + 1
        row = row + 1
        col = 1
    logger.warning(f"The marker cell {marker} wasn't found")
    return None, None

def parse_string_list_in_line(sheet, row, col_start):
    "Parse a line representing a list of strings"
    "(stop at the first empty cell)"

    result = []
    col = col_start
    while True:
        val = string_cell(sheet, row, col)
        if val == '':
            break
        result.append(val)
        col = col + 1

    return result

def parse_dictionary(sheet, row_start, col_start, row_end = REASONABLE):
    "Parse a block, turning it into a dictionary of string lists"
    "The first column gives the keys, the line at the right of the key is"
    "the associated value"
    result = dict()
    row = row_start
    while row < row_end:
        name = string_cell(sheet, row, col_start)
        if name == '':
            row = row + 1
            continue
        if name in result:
            logger.warning(f"At row {row:d}, key {name} is a duplicate: ignoring the line")
            row = row + 1
            continue
        result[name] = parse_string_list_in_line(sheet, row, col_start + 1)
        row = row + 1
    print(f"Starting at {row_start}: {result}") # FIXME: debug output
    return result

def parse_rooms(sheet):
    row_groups, col_groups = find_cell(sheet, '[GROUPES]')
    row_cats, col_cats = find_cell(sheet, '[CATÉGORIES]')
    if col_groups != col_cats or row_cats < row_groups:
        logger.warning(f"The marker cells in sheet {rooms_sheet} are misplaced")
        return set(), dict(), dict()

    #
    # parse the groups
    #
    groups = dict()
    pre_groups = parse_dictionary(sheet, row_groups + 1, col_groups, row_cats)

    # drop empty groups
    empty = set() # empty groups
    for name, lst in pre_groups.items():
        if len(lst) == 0:
            empty.add(name)
    if len(empty) > 0:
        logger.warning("Some groups of rooms are empty, hence ignored: {0:s}".format(', '.join(empty)))
        for solo in empty:
            del pre_groups[solo]

    # don't accept group names in groups
    group_names = pre_groups.keys()
    for name, lst in pre_groups.items():
        bad = set.intersection(set(lst), group_names)
        if len(bad) > 0:
            logger.warning("Group '{0:s}' contains group names, ignoring them: {1:s}".format(name,', '.join(bad)))
            groups[name] = set.difference(set(lst), group_names)
        else:
            groups[name] = set(lst)

    #
    # parse the categories
    #
    categories = dict()
    pre_cats = parse_dictionary(sheet, row_cats + 1, col_cats)

    # drop empty categories
    empty = set() # empty groups
    for name, lst in pre_cats.items():
        if len(lst) == 0:
            empty.add(name)
    if len(empty) > 0:
        logger.warning("Some categories of rooms are empty, hence ignored: {0:s}".format(', '.join(empty)))
        for solo in empty:
            del pre_cats[solo]

    # don't accept category names in categories
    cat_names = pre_cats.keys()
    for name, lst in pre_cats.items():
        bad = set.intersection(set(lst), cat_names)
        if len(bad) > 0:
            logger.warning("Category '{0:s}' contains category names, ignoring them: {1:s}".format(name,', '.join(bad)))
            categories[name] = set.difference(set(lst), cat_names)
        else:
            categories[name] = set(lst)

    #
    # Build the set of rooms
    #
    rooms = set()
    for lst in groups.values():
        rooms.update(lst)
    for lst in categories.values():
        rooms.update(lst)
    rooms.difference_update(group_names)
    rooms.difference_update(cat_names)
            
    return rooms, groups, categories

def parse_people(sheet):
    row, col = find_cell(sheet, "[Identifiant]")
    if row == None:
        logger.warning(f"The marker cell in sheet {people_sheet} is missing")
        return dict()

    row = row + 1
    result = dict()
    while row < REASONABLE:
        id_ = string_cell(sheet, row, col)
        if id_ == '':
            row = row + 1
            continue
        if id_ in result:
            logger.warning(f"Duplicate identifier '{id_}' in row {row}: ignoring the line")
            row = row + 1
            continue
        result[id_] = {'nom': string_cell(sheet, row, col + 1),
                       'prenom': string_cell(sheet, row, col + 2),
                       'adresse': string_cell(sheet, row, col + 3),
                       'statut': string_cell(sheet, row, col + 4),
                       'employeur': string_cell(sheet, row, col + 5)}
        row = row + 1
    return result

def parse_file(filename = 'file_essai.xlsx'):
    try:
        wb = load_workbook(filename)
        
        sheet = wb[rooms_sheet]
        if not sheet:
            pass # FIXME: do something

        print("========= WARNINGS ============")

        rooms, groups, categories = parse_rooms(sheet)

        print("========= RESULT ============")
        print("rooms: ", rooms) # FIXME: debug output
        print("groups: ", groups) # FIXME: debug output
        print("catégories: ", categories) # FIXME: debug output


        sheet = wb[people_sheet]
        if not sheet:
            pass # FIXME: do something

        print("========= WARNINGS ============")

        people = parse_people(sheet)

        print("========= RESULT ============")
        print(f"{people=}" ) # FIXME: debug output
        
    except FileNotFoundError as ex:
        logger.warning("Database file couldn't be opened: ", ex)

parse_file() # FIXME: for debug
