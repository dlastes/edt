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

import importlib
from TTapp.TTModel import TTModel

from MyFlOp.MyTTUtils import print_differences


class MyTTModel(TTModel):
    def __init__(self, department_abbrev, weeks, year,
                 train_prog=None,
                 stabilize_work_copy=None,
                 min_bhd_g=0.5):
        TTModel.__init__(self, department_abbrev, weeks, year,
                         train_prog=train_prog,
                         stabilize_work_copy=stabilize_work_copy,
                         min_bhd_g=min_bhd_g)

    def add_specific_constraints(self):
        """
        The speficic constraints stored in the database are added by the
        TTModel class.
        If you shall add more specific ones, you may write it down here.
        """
        TTModel.add_specific_constraints(self)

    def solve(self, time_limit=3600, target_work_copy=None,
              solver='gurobi'):
        """
        If you shall add pre (or post) processing apps, you may write them down
        here.
        """
        result = TTModel.solve(self,
                               time_limit=time_limit,
                               target_work_copy=target_work_copy,
                               solver=solver)
        if result is None:
            spec = importlib.util.find_spec('gurobipy')
            if spec:
                from gurobipy import read
                lp = "FlOpTT-pulp.lp"
                m = read(lp)
                # m.optimize()
                m.computeIIS()
                m.write("logs/IIS_weeks%s.ilp" % self.weeks)
                print("IIS written in file logs/IIS_week%s.ilp" % (self.weeks))
        else :
            if self.stabilize_work_copy is not None:
                print_differences(self.weeks, self.year, self.stabilize_work_copy, target_work_copy, self.wdb.instructors)
