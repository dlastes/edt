#!/usr/bin/env python3
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

from base.models import Day

nb_salaries = {'A': {}, 'B': {}}
nb_salaries['A'][Day.MONDAY] = {7: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 0},
                                8: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 1},
                                9: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 1},
                                10: {'Proj': 0.5, 'Caisse': 0, 'Ct/Mén': 1},
                                11: {'Proj': 1, 'Caisse': 0, 'Ct/Mén': 0},
                                12: {'Proj': 1, 'Caisse': 0, 'Ct/Mén': 0},
                                13: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                14: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                15: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                16: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                17: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                18: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                19: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                20: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                21: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                22: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                23: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 0},
                                24: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 0}
                                }
nb_salaries['A'][Day.TUESDAY] = {7: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 0},
                                8: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 1},
                                9: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 1},
                                10: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 1},
                                11: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 0},
                                12: {'Proj': 0.5, 'Caisse': 0, 'Ct/Mén': 0},
                                13: {'Proj': 1, 'Caisse': 0, 'Ct/Mén': 0},
                                14: {'Proj': 1, 'Caisse': 0, 'Ct/Mén': 0},
                                15: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                16: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                17: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                18: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                19: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                20: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                21: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                22: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                23: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                24: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 0}
                                }
nb_salaries['A'][Day.WEDNESDAY] = {7: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 0},
                                8: {'Proj': 1, 'Caisse': 0, 'Ct/Mén': 1},
                                9: {'Proj': 1, 'Caisse': 0, 'Ct/Mén': 1},
                                10: {'Proj': 1, 'Caisse': 0, 'Ct/Mén': 1},
                                11: {'Proj': 1, 'Caisse': 0, 'Ct/Mén': 0},
                                12: {'Proj': 1, 'Caisse': 0, 'Ct/Mén': 0},
                                13: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                14: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                15: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                16: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                17: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                18: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                19: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                20: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                21: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                22: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                23: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 0},
                                24: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 0}
                                }
nb_salaries['A'][Day.THURSDAY] = {7: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 0},
                                8: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 1},
                                9: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 1},
                                10: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 1},
                                11: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 0},
                                12: {'Proj': 0.5, 'Caisse': 0, 'Ct/Mén': 0},
                                13: {'Proj': 1, 'Caisse': 0, 'Ct/Mén': 0},
                                14: {'Proj': 1, 'Caisse': 0, 'Ct/Mén': 0},
                                15: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                16: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                17: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                18: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                19: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                20: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                21: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                22: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                23: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                24: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 0}
                                }
nb_salaries['A'][Day.FRIDAY] = {7: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 0},
                                8: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 1},
                                9: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 1},
                                10: {'Proj': 0.5, 'Caisse': 0, 'Ct/Mén': 1},
                                11: {'Proj': 1, 'Caisse': 0, 'Ct/Mén': 0},
                                12: {'Proj': 1, 'Caisse': 0, 'Ct/Mén': 0},
                                13: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                14: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                15: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                16: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                17: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                18: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                19: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 1},
                                20: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 1},
                                21: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 1},
                                22: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                23: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                24: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 0}
                                }
nb_salaries['A'][Day.SATURDAY] = {7: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 0},
                                8: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 1},
                                9: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 1},
                                10: {'Proj': 0.5, 'Caisse': 0, 'Ct/Mén': 1},
                                11: {'Proj': 1, 'Caisse': 0, 'Ct/Mén': 0},
                                12: {'Proj': 1, 'Caisse': 0, 'Ct/Mén': 0},
                                13: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                14: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                15: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                16: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                17: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                18: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                19: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 1},
                                20: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 1},
                                21: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 1},
                                22: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                23: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                24: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 0}
                                }
nb_salaries['A'][Day.SUNDAY] = {7: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 0},
                                8: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 1},
                                9: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 1},
                                10: {'Proj': 0.5, 'Caisse': 0, 'Ct/Mén': 1},
                                11: {'Proj': 1, 'Caisse': 0, 'Ct/Mén': 0},
                                12: {'Proj': 1, 'Caisse': 0, 'Ct/Mén': 0},
                                13: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                14: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                15: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 1},
                                16: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 1},
                                17: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 1},
                                18: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 1},
                                19: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                20: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                21: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                22: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                23: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 0},
                                24: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 0}
                                }

for day in [c[0] for c in Day.CHOICES]:
    nb_salaries['B'][day] = {7: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 0},
                                8: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 1},
                             9: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 1},
                             10: {'Proj': 0.5, 'Caisse': 0, 'Ct/Mén': 1},
                                11: {'Proj': 1, 'Caisse': 0, 'Ct/Mén': 0},
                                12: {'Proj': 1, 'Caisse': 0, 'Ct/Mén': 0},
                                13: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                14: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                15: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 1},
                                16: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 1},
                                17: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 1},
                                18: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 1},
                                19: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 1},
                                20: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 1},
                                21: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                22: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                23: {'Proj': 1, 'Caisse': 1, 'Ct/Mén': 0},
                                24: {'Proj': 0, 'Caisse': 0, 'Ct/Mén': 0}
                                }


