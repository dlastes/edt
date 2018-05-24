from modif.weeks import week_list
from modif.models import Cours, ModuleDisplay
from django.core.exceptions import ObjectDoesNotExist

import json


def assign_color():
    """
    Assign a color to each module.
    :return:
    """
    wl = week_list()

    # find the biggest number of simultaneous modules
    module_max = 0
    motley = -1
    for wy in wl:
        number_modules = Cours.objects.filter(semaine = wy['semaine'],
                                              an = wy['an'])\
            .distinct('module').count()
        if number_modules > module_max:
            motley = wl.index(wy)
            module_max = number_modules

    free_colors = get_color_set('modif/static/modif/colors.json', module_max)
    taken_colors = []

    for wi in range(motley, -1, -1) + range(motley + 1, len(wl) + 1):
        module_to_assign = []
        for c in Cours.objects.filter(semaine = wl[wi]['semaine'],
                                      an = wl[wi]['an']).distinct('module'):
            try:
                module_display = ModuleDisplay.objects.get(module = c.module)
                free_colors.remove(module_display.color)
                taken_colors.append(module_display.color)
            except ObjectDoesNotExist:
                module_to_assign.append(c.module)
        for m in module_to_assign:
            color = free_colors.pop()
            taken_colors.append(color)
            module_display = ModuleDisplay(module = m, color = color)
            module_display.save()
        free_colors += taken_colors








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
            if len(init_color_set) > len(color_set):
                if len(color_set) < target_nb_colors:
                    color_set = init_color_set
            else:
                if len(init_color_set) >= target_nb_colors:
                    color_set = init_color_set

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
