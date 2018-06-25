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

from __future__ import absolute_import, unicode_literals
from celery import shared_task
from people.models import FullStaff
from StringIO import StringIO
from channels import Channel
import os
from django.conf import settings
import sys
from MyFlOp.MyTTModel import MyTTModel
from modif.models import TrainingProgramme
from django.core.exceptions import ObjectDoesNotExist

@shared_task
def run(week, year, timestamp, train_prog, msg_reply):
    try:
        tp = TrainingProgramme.objects.get(abbrev=train_prog)
    except ObjectDoesNotExist:
        tp = None

    out = Tee(str(year)+ '-' + str(week) + '--'
              + timestamp + '.log', msg_reply)
    sys.stdout = out
    sys.stderr = out
    try:
        t = MyTTModel(week, year, train_prog=tp)
        t.solve()
    finally:
        out.close()
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__



class Tee(StringIO):                      
    def __init__(self, fn, msg_reply):
        self.chan = Channel(msg_reply)
        self.file = open(os.path.join(settings.BASE_DIR,
                                      'logs',
                                      fn), 'w')
        self.chan.send({'text':'Solver fired.'})
        
    def write(self, s):
        self.chan.send({'text':s})
        self.file.write(s)
        sys.__stdout__.write(s)

    def close(self):
        self.chan.send({'text': u'Solver ended.'})
        self.file.close()
        

# celery -A FlOpEDT worker -l info
