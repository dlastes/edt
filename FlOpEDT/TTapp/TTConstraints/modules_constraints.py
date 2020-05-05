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


from django.db import models

from TTapp.helpers.minhalfdays import MinHalfDaysHelperModule

from TTapp.TTconstraint import TTConstraint


class MinModulesHalfDays(TTConstraint):
    """
    All courses will fit in a minimum of half days
    """
    modules = models.ManyToManyField('base.Module', blank=True)

    def enrich_model(self, ttmodel, week, ponderation=1):

        if self.modules.exists():
            helper = MinHalfDaysHelperModule(ttmodel, self, week, ponderation)
            for module in self.modules.all():
                helper.enrich_model(module=module)

        else:
            print("MinHalfDays must have at least  one module --> Ignored")
            return

    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        details = view_model['details']

        if self.modules.exists():
            details.update({'modules': ', '.join([module.abbrev for module in self.modules.all()])})

        return view_model

    def one_line_description(self):
        text = "Minimise les demie-journées"

        if self.modules.exists():
            text += ' de : ' + ', '.join([str(module) for module in self.modules.all()])

        if self.train_progs.exists():
            text += ' en ' + ', '.join([train_prog.abbrev for train_prog in self.train_progs.all()])

        return text
