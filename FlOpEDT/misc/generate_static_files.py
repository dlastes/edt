# coding: utf8
# -*- coding: utf-8 -*-

# This file is part of the FlOpEDT/FlOpScheduler project.
# Copyright (c) 2017
# Authors: Iulian Ober, Paul Renaud-Goud, Pablo Seban, et al.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program. If not, see
# <http://www.gnu.org/licenses/>.
#
# You can be released from the requirements of the license by purchasing
# a commercial license. Buying such a license is mandatory as soon as
# you develop activities involving the FlOpEDT/FlOpScheduler software
# without disclosing the source code of your own applications.

from base.models import Group, TrainingProgramme, GroupDisplay, \
    TrainingProgrammeDisplay

from base.models import Room, RoomType, RoomGroup, RoomSort

from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

import json
import os


def generate_group_file():
    """
    From the data stored in the database, fill the group description file, that
    will be used by the website
    :return:
    """
    final_groups = []

    for train_prog in TrainingProgramme.objects.all():

        gp_dict_children = {}
        gp_master = None
        for gp in Group.objects.filter(train_prog=train_prog):
            if gp.full_name() in gp_dict_children:
                raise Exception('Group name should be unique')
            if gp.parent_groups.all().count() == 0:
                if gp_master is not None:
                    raise Exception('One single group is able to be without '
                                    'parents')
                gp_master = gp
            elif gp.parent_groups.all().count() > 1:
                raise Exception('Not tree-like group structures are not yet '
                                'handled')
            gp_dict_children[gp.full_name()] = []

        for gp in Group.objects.filter(train_prog=train_prog):
            for new_gp in gp.parent_groups.all():
                gp_dict_children[new_gp.full_name()].append(gp)

        final_groups.append(get_descendant_groups(gp_master, gp_dict_children))

    with open(os.path.join(settings.BASE_DIR, 'base', 'static', 'base',
                           'groups.json'), 'w') as fp:
        json.dump(final_groups, fp)


def get_descendant_groups(gp, children):
    """
    Gather informations about all descendants of a group gp
    :param gp:
    :param children: dictionary <group_full_name, list_of_children>
    :return: an object containing the informations on gp and its descendants
    """
    current = {}
    if not gp.parent_groups.all().exists():
        current['parent'] = 'null'
        tp = gp.train_prog
        current['promo'] = tp.abbrev
        try:
            tpd = TrainingProgrammeDisplay.objects.get(training_programme=tp)
            if tpd.short_name != '':
                current['promotxt'] = tpd.short_name
            else:
                current['promotxt'] = tp.abbrev
            current['row'] = tpd.row
        except ObjectDoesNotExist:
            raise Exception('You should indicate on which row a training '
                            'programme will be displayed '
                            '(cf TrainingProgrammeDisplay)')
    current['name'] = gp.nom
    try:
        gpd = GroupDisplay.objects.get(group=gp)
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


def generate_room_file():
    """
    From the data stored in the database, fill the room description file, that
    will be used by the website
    :return:
    """
    d = {}
    for rt in RoomType.objects.all():
        d[str(rt)] = []
        for rg in rt.members.all():
            for r in rg.subrooms.all():
                if str(r) not in d[str(rt)]:
                    d[str(rt)].append(str(r))
    
    with open(os.path.join(settings.BASE_DIR, 'base',
                           'static', 'base',
                           'rooms.json'), 'w') as fp:
        json.dump(d, fp)

    return d
            
                
        
