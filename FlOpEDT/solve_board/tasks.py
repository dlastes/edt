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
#from celery import shared_task
from people.models import FullStaff
from StringIO import StringIO
from channels import Channel
import os
from django.conf import settings
import sys

from .modified_capturer import CaptureOutput

# @shared_task
# def run(week, year, timestamp, train_prog, msg_reply):
#     try:
#         tp = TrainingProgramme.objects.get(abbrev=train_prog)
#     except ObjectDoesNotExist:
#         tp = None
#
#     # out = Tee(str(year)+ '-' + str(week) + '--'
#     #           + timestamp + '.log', msg_reply)
#     # sys.stdout = out
#     # sys.stderr = out
#     # try:
#     #     t = MyTTModel(week, year, train_prog=tp)
#     #     t.solve()
#     # finally:
#     #     out.close()
#     #     sys.stdout = sys.__stdout__
#     #     sys.stderr = sys.__stderr__
#
#     with CaptureOutput(relay=False) as cap:
#         t = MyTTModel(week, year, train_prog=tp)
#         t.solve()
#         cap.save_to_path('home/prenaud/trash/modcap.log')
        


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
        






# GRACEFUL_SHUTDOWN_SIGNAL = signal.SIGUSR1
# """
# The number of the UNIX signal used to communicate graceful shutdown requests
# from the main process to the output relay process (an integer). See also
# :func:`~MultiProcessHelper.enable_graceful_shutdown()`.
# """


# class Broadcast(object):
#     def __init__(self, chunk_size=1024):
#         self.master_fd, self.slave_fd = pty.openpty()
#         print self.master_fd
#         print self.slave_fd
        
#         self.chunk_size = chunk_size
        
#     def start_capture(self):
#         """
#         Start a child process using :class:`multiprocessing.Process`.

#         :param target: The callable to run in the child process. Expected to
#                        take a single argument which is a
#                        :class:`multiprocessing.Event` to be set when the child
#                        process has finished initialization.
#         """
#         started_event = billiard.Event()
#         self.capture_process = billiard.Process(target=self.capture_loop, args=(started_event,))
#         #self.capture_process.daemon = True
#         self.capture_process.start()
#         started_event.wait()

#     def stop_capture(self):
#         """
#         Gracefully shut down all child processes.

#         Child processes are expected to call :func:`enable_graceful_shutdown()`
#         during initialization.
#         """
#         if self.capture_process.is_alive():
#             os.kill(self.capture_process.pid, GRACEFUL_SHUTDOWN_SIGNAL)
#         self.capture_process.join()
#         self.close_pseudo_terminal()

#     def close_pseudo_terminal(self):
#         """Close the pseudo terminal's master/slave file descriptors."""
#         for name in ('master_fd', 'slave_fd'):
#             fd = getattr(self, name)
#             if fd is not None:
#                 os.close(fd)
#                 setattr(self, name, None)

    
#     def enable_graceful_shutdown(self):
#         """
#         Register a signal handler that converts :data:`GRACEFUL_SHUTDOWN_SIGNAL` to an exception.

#         Used by :func:`~PseudoTerminal.capture_loop()` to gracefully interrupt
#         the blocking :func:`os.read()` call when the capture loop needs to be
#         terminated (this is required for coverage collection).
#         """
#         signal.signal(GRACEFUL_SHUTDOWN_SIGNAL, self.raise_shutdown_request)


#     def capture_loop(self, started_event):
#         """
#         Continuously read from the master end of the pseudo terminal and relay the output.

#         This function is run in the background by :func:`start_capture()`
#         using the :mod:`multiprocessing` module. It's role is to read output
#         emitted on the master end of the pseudo terminal and relay this output
#         to the real terminal (so the operator can see what's happening in real
#         time) as well as a temporary file (for additional processing by the
#         caller).
#         """
#         self.enable_graceful_shutdown()
#         print 'qweqweqweqweqwe'
#         started_event.set()
#         print 'oiheohieoe'
#         try:
#             print 'qwoeqoqpojjeoje'
#             while True:
#                 # Read from the master end of the pseudo terminal.
#                 output = os.read(self.master_fd, self.chunk_size)
#                 print 'gaga' + output
#                 if output:
#                     self.fd.write(output)
#                 else:
#                     # Relinquish our time slice, or in other words: try to be
#                     # friendly to other processes when os.read() calls don't
#                     # block. Just for the record, all of my experiments have
#                     # shown that os.read() on the master file descriptor
#                     # returned by pty.openpty() does in fact block.
#                     time.sleep(0)
#         except ShutdownRequested:
#             print 'shuuuuut'
#             pass
#         print 'graaaaa'
        

#     def raise_shutdown_request(self, signum, frame):
#         """Raise :exc:`ShutdownRequested` when :data:`GRACEFUL_SHUTDOWN_SIGNAL` is received."""
#         raise ShutdownRequested
        
#     def __enter__(self):
#         """Automatically call :func:`start_capture()` when entering a :keyword:`with` block."""
#         self.fd = open('/home/prenaud/trash/capcap.log', 'w')
#         self.start_capture()
#         return self

#     def __exit__(self, exc_type=None, exc_value=None, traceback=None):
#         """Automatically call :func:`finish_capture()` when leaving a :keyword:`with` block."""
#         self.stop_capture()
#         self.fd.close()
    
# # celery -A FlOpEDT worker -l info

# class ShutdownRequested(Exception):

#     """
#     Raised by :func:`~MultiProcessHelper.raise_shutdown_request()` to signal
#     graceful termination requests (in :func:`~PseudoTerminal.capture_loop()`).
#     """

