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




from django.shortcuts import render
from django.http import HttpResponse
from MyFlOp import MyTTUtils

# Create your views here.

def viewForm(request, funcname):
    resp = '<form>'
    for i in MyTTUtils.funcTab:
        print(funcname)
        if i.get('func_name') == funcname:
            print(i.get('func_name'))
            args = i.get('args')
            for y in args:
                resp += '<label>' + y + '</label><input name="'+ y + '" type="text"/>'
    
    resp += '<button>Submit</button>'
    resp += '</form>'
    return HttpResponse(resp)

def submitForm(request, funcname):
    request.POST['']
    func = ''
    args = ''
    finalargs = {}
    for i in MyTTUtils.funcTab:
        if i.get('func_name') == funcname:
            func = i.get('func')
            args = i.get('args')
