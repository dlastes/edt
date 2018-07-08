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

# from django.http import HttpResponse
# from channels.handler import AsgiHandler
from channels import Group, Channel
# from tasks import run
import json
from threading import Thread
from .modified_capturer import CaptureOutput
from django.core.exceptions import ObjectDoesNotExist
from MyFlOp.MyTTModel import MyTTModel
from modif.models import TrainingProgramme
# from multiprocessing import Process
import os
from django.conf import settings


def ws_message(message):
    # ASGI WebSocket packet-received and send-packet message types
    # both have a "text" key for their textual data.
    # message.reply_channel.send({
    #     "text": message.content['text'],
    # })
    msg_reply = message.reply_channel.name
    data = json.loads(message['text'])
    Channel(msg_reply).send({'text':data['text']})
    if data['action'] == 'go':
        # run.delay(data['week'],data['year'],
        #           data['timestamp'],
        #           data['train_prog'],
        #           message.reply_channel.name)

        Solve(data['week'],data['year'],
                  data['timestamp'],
                  data['train_prog'],
        Channel(msg_reply)).start()

        # p = Process(target=ruru, args=(data['week'],data['year'],Channel(msg_reply)))
        # p.start()


class Solve(Thread):
    def __init__(self, week, year, timestamp, training_programme, chan):
        super(Solve, self).__init__()
        self.week = week
        self.year = year
        self.timesamp = timestamp
        self.channel = chan
        # if all train progs are called, training_programme=''
        try:
            self.training_programme = TrainingProgramme.objects.get(abbrev=training_programme)
        except ObjectDoesNotExist:
            self.training_programme = None
        
    
    def run(self):
        print 'start running'
        with CaptureOutput(relay=False, channel=self.channel) as cap:
            t = MyTTModel(self.week, self.year, train_prog=self.training_programme)
            t.solve(time_limit=20)
            cap.save_to_path(os.path.join(settings.BASE_DIR,
                                          'logs',
                                          str(year)+ '-' + str(week) + '--'
                                          + timestamp + '.log'))
        print 'stop running'



def ruru(week, year, channel):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FlOpEDT.settings.local")
    print 'start running'
    with CaptureOutput(relay=False, channel=channel) as cap:
        print week
        print year
        print channel
        print 'qqweqw'
        
        t = MyTTModel(week, year)
        t.solve(time_limit=20)
        cap.save_to_path('/home/prenaud/trash/modcap.log')
    print 'stop running'
    

        
# Connected to websocket.connect
def ws_add(message):
    # Accept the incoming connection
    message.reply_channel.send({"accept": True})
    # # Add them to the chat group
    # Group("solver").add(message.reply_channel)


# Connected to websocket.disconnect
# def ws_disconnect(message):
#     Group("solver").discard(message.reply_channel)




# https://vincenttide.com/blog/1/django-channels-and-celery-example/
# http://docs.celeryproject.org/en/master/django/first-steps-with-django.html#django-first-steps
# http://docs.celeryproject.org/en/master/getting-started/next-steps.html#next-steps



# send a signal
# https://stackoverflow.com/questions/15080500/how-can-i-send-a-signal-from-a-python-program#20972299
# output file+console
# https://stackoverflow.com/questions/11325019/output-on-the-console-and-file-using-python
# redirect pulp
# https://stackoverflow.com/questions/26642029/writing-coin-or-cbc-log-file
# start function in new process
# https://stackoverflow.com/questions/7207309/python-how-can-i-run-python-functions-in-parallel#7207336
# generate uuid: import uuid ; uuid.uuid4()



# channel init
# https://blog.heroku.com/in_deep_with_django_channels_the_future_of_real_time_apps_in_django


# moving to production
# https://channels.readthedocs.io/en/1.x/backends.html
# port 6379?






# docker image
# sudo apt-get install redis-server
