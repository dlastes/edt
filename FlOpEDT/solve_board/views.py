# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from modif import weeks

from solve_board.models import SolveRun

from django.contrib.admin.views.decorators import staff_member_required

from django.http import Http404, JsonResponse

from multiprocessing import Process

from channels import Group

@staff_member_required
def main_board(req):
    return render(req,
                  'solve_board/main-board.html',
                  {'all_weeks': weeks.week_list(),
                   'start_date': weeks.current_week(),
                   'end_date': weeks.current_week(),
                   'current_year': weeks.annee_courante})


def run(req, timestamp):
    ret = {'text': 'Solveur : Allô', 'pid': 0}
    if req.GET:
        start_week = int(req.GET.get('sw','0'))
        start_year = int(req.GET.get('sy','0'))
        end_week = int(req.GET.get('ew','0'))
        end_year = int(req.GET.get('ey','0'))
    else:
        ret.text = 'Sorry ?'
        return JsonResponse(ret)
    if start_week == 0 or start_year == 0 or end_week == 0 or end_year == 0:
        ret.text = "Parameters issue. 0 or not provided..."
        return JsonResponse(ret)
        
    sr = SolveRun(run_label=timestamp,
                  start_week=start_week,
                  start_year=start_year,
                  end_week=end_week,
                  end_year=end_year)

    p = Process(target=spawn_solve, args=(timestamp,Group('solver')))
    p.start()
    sr.pid = p.pid
    sr.save()
    ret['pid'] = p.pid
    
    return JsonResponse(ret)


def spawn_solve(timestamp, g):
    print "iiin"
    print g
    print timestamp
    s = g.send({
        "text": timestamp
    })
    print s
    for i in range(10):
        Group("solver").send({
            "text": str(i),
        })
