from modif.models import Group, TrainingProgramme, GroupDisplay, \
    TrainingProgrammeDisplay
from django.core.exceptions import ObjectDoesNotExist
import json
import os

def generate_group_file():

    final_groups = []

    for train_prog in TrainingProgramme.objects.all():

        gp_dict_children = {}
        gp_master = None
        for gp in Group.objects.filter(train_prog = train_prog):
            if gp.full_name() in gp_dict_children:
                raise Exception('Group name should be unique')
            if len(gp.parent_groups) == 0:
                if gp_master is not None:
                    raise Exception('One single group is able to be without '
                                    'parents')
                gp_master = gp
            elif len(gp.parent_groups) > 1:
                raise Exception('Not tree-like group structures are not yet '
                                'handled')
            gp_dict_children[gp.full_name()] = []

        for gp in Group.objects.filter(train_prog = train_prog):
            for new_gp in gp.parent_groups:
                gp_dict_children[new_gp.full_name()].append(gp)

        final_groups.append(get_descendant_groups(gp_master, gp_dict_children))

    with open(os.path.join('modif', 'static', 'modif',
                           'groups.json'), 'w') as fp:
        json.dump(final_groups, fp)


def get_descendant_groups(gp, children):
    current = {}
    if len(gp.surgroupe) == 0:
        current['parent'] = 'null'
        tp = gp.train_prog
        current['promo'] = tp.abbrev
        try:
            tpd = TrainingProgrammeDisplay.objects.get(training_programme = tp)
            current['row'] = tpd.row
        except ObjectDoesNotExist:
            raise Exception('You should indicate on which row a training '
                            'programme will be displayed '
                            '(cf TrainingProgrammeDisplay)')
    current['name'] = gp.nom
    try:
        gpd = GroupDisplay.objects.get(group = gp)
        if gpd.button_height is not None:
            current['buth'] = gpd.button_height
        if gpd.button_txt is not None:
            current['buttxt'] = gpd.button_txt
    except ObjectDoesNotExist:
        pass

    if len(children[gp.full_name()]) > 0:
        current['children'] = []
        for gp_child in children[gp.full_name()]:
            gp_obj = get_descendant_groups(gp_child, children)
            gp_obj['parent'] = gp.nom
            current['children'].append(gp_obj)

    return current