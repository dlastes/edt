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

from modif.weeks import week_list
from modif.models import Cours, ModuleDisplay, TrainingProgramme, Module
from django.core.exceptions import ObjectDoesNotExist
from pyclustering.gcolor.dsatur import dsatur
from numpy import diag, eye

import json
import os


def assign_color(overwrite = True, diff_across_train_prog = False):
    """
    Assigns a color to each module
    :param overwrite: if overwrite, overwrites all preexisting colors,
    otherwise does not touch the existing colors, but considers that they do not
    belong to the colors chosen in colors.json
    :param diff_across_train_prog: if diff_across_train_prog, it is required
    that two simultaneous modules should wear different colors even if they
    belong to different training programmes
    :return:
    """
    if diff_across_train_prog:
        keys, mat = build_graph_matrices(None)
        optim_and_save(keys, mat, overwrite)
    else:
        for train_prog in TrainingProgramme.objects.all():
            print train_prog
            keys, mat = build_graph_matrices(train_prog)
            optim_and_save(keys, mat, overwrite)


def optim_and_save(keys, mat, overwrite):
    opti = dsatur(mat)
    opti.process()
    color_indices = opti.get_colors()
    print color_indices, max(color_indices)
    color_set = get_color_set(os.path.join('misc', 'colors.json'),
                              max(color_indices))
    for mi in range(len(keys)):
        cbg = color_set[color_indices[mi]-1]
        try:
            mod_disp = ModuleDisplay.objects.get(module = keys[mi])
            if overwrite:
                mod_disp.color_bg = cbg
                mod_disp.color_txt = compute_luminance(cbg)
                mod_disp.save()
        except ObjectDoesNotExist:
            mod_disp = ModuleDisplay(module = keys[mi],
                                     color_bg = cbg,
                                     color_txt = compute_luminance(cbg))
            mod_disp.save()


def build_graph_matrices(train_prog = None):
    if train_prog is None:
        keys = list(Module.objects.all())
    keys = list(Module.objects.filter(train_prog = train_prog))
    mat = eye(len(keys))
    wl = week_list()

    for mi in range(len(keys)):
        for mj in range(mi+1, len(keys)):
            for wy in wl:
                if Cours.objects.filter(semaine = wy['semaine'],
                                        an = wy['an'],
                                        module__in = [keys[mi], keys[mj]])\
                        .distinct('module').count() == 2:
                    mat[(mi, mj)] = 1
                    break
    mat += mat.T - diag(mat.diagonal())
    return keys, mat


def get_color_set(filename, target_nb_colors):
    """
    Builds a color set from a json file which contains a list of
    {"tot": number_of_colors, "colors": list of colors maximizing the
    perceptual distance within the list}, cf http://vrl.cs.brown.edu/color.
    :param filename: the colors.json
    :param target_nb_colors: minimum number of colors
    :return: a set of colors, not smaller than needed
    """
    color_set = ["red"]
    with open(filename) as json_data:
        initial_colors = json.load(json_data)

        # find smallest set, bigger than needed
        # otherwise just the biggest
        for init_color_set in initial_colors:
            if len(init_color_set['colors']) > len(color_set):
                if len(color_set) < target_nb_colors:
                    color_set = init_color_set['colors']
            else:
                if len(init_color_set['colors']) >= target_nb_colors:
                    color_set = init_color_set['colors']

        print color_set

        # extend the color set if needed
        if len(color_set) < target_nb_colors:
            sliced = color_set[:]
            add_factor = target_nb_colors / len(color_set)
            for i in range(add_factor):
                color_set += sliced
            # shrink the color set if needed
            if len(color_set) > target_nb_colors:
                color_set = color_set[len(color_set) - target_nb_colors:]

    return color_set


def compute_luminance(col):
    hexa = col[1:]
    perceived_luminance = 0.299 * int('0x' + hexa[0:2], 16) \
                          + 0.587 * int('0x' + hexa[2:4], 16) \
                          + 0.114 * int('0x' + hexa[4:6], 16)
    if perceived_luminance < 127.5:
        return '#FFFFFF'
    else:
        return '#000000'



# def compute_luminance(l):
#     color_txt = []
#     for el in l:
#         hexa = el[1:]
#         perceived_luminance = 0.299 * int('0x' + hexa[0:2], 16) \
#                               + 0.587 * int('0x' + hexa[2:4], 16) \
#                               + 0.114 * int('0x' + hexa[4:6], 16)
#         if perceived_luminance < 127.5:
#             color_txt.append('#FFFFFF')
#         else:
#             color_txt.append('#000000')
#     return color_txt




#     wl = week_list()
#
#     for train_prog in TrainingProgramme.objects.all():
#         # find the biggest number of simultaneous modules
#         module_max = 0
#         motley = -1
#         for wy in wl:
#             number_modules = Cours.objects.filter(
#                 semaine = wy['semaine'],
#                 an = wy['an'],
#                 groupe__train_prog = train_prog)\
#                 .distinct('module').count()
#             if number_modules > module_max:
#                 motley = wl.index(wy)
#                 module_max = number_modules
#
#         print train_prog, module_max
#
#         all_colors = get_color_set('modif/static/modif/colors.json',
#                                     module_max)
#         txt_colors = compute_luminance(all_colors)
#         all_colors = zip(all_colors, txt_colors)
#         print len(all_colors)
#
#         for wi in range(motley, -1, -1) + range(motley + 1, len(wl)):
#             module_to_assign = []
#             free_colors = all_colors[:]
#             taken = []
#             print wi, len(wl), len(free_colors)
#             for c in Cours.objects.filter(
#                     semaine = wl[wi]['semaine'],
#                     an = wl[wi]['an'],
#                     groupe__train_prog = train_prog)\
#                     .distinct('module'):
#                 try:
#                     module_display = ModuleDisplay.objects\
#                         .get(module = c.module)
#                     for col in free_colors:
# #                        print col[0], module_display.color_bg
#                         if col[0] == module_display.color_bg:
#                             pair = col
#                             print 'found'
#                             break
#                     #print len(free_colors)
#                     try:
#                         free_colors.remove(pair)
#                         taken.append(pair)
#                     except:
#                         print 'WTF where is'
#                         print module_display.color_bg
#                         print free_colors
#                         print taken
#                         return
#                     #print len(free_colors)
#                 except ObjectDoesNotExist:
#                     module_to_assign.append(c.module)
#
#             for m in module_to_assign:
#                 color = free_colors.pop()
#                 module_display = ModuleDisplay(module = m,
#                                                color_bg = color[0],
#                                                color_txt = color[1])
#                 module_display.save()
#                 #print module_display
