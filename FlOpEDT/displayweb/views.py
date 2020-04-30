from django.shortcuts import render

from django.http import HttpResponse

from FlOpEDT.settings.base import COSMO_MODE

from people.models import Tutor
from base.models import Module, ScheduledCourse
from displayweb.models import TutorDisplay, ModuleDisplay
from displayweb.admin import TutorDisplayResource, ModuleDisplayResource

# Create your views here.
def fetch_rectangle_colors(req, **kwargs):
    #if not req.is_ajax() or req.method != "GET":
    #    return HttpResponse("KO")
    week = req.GET.get('week', None)
    year = req.GET.get('year', None)
    work_copy = int(req.GET.get('work_copy', '0'))
    filters = {}
    if COSMO_MODE:
        Display = TutorDisplay.objects
        Resource = TutorDisplayResource
    else:
        Display = ModuleDisplay.objects
        Resource = ModuleDisplayResource
    if week is None or year is None:
        if COSMO_MODE:
            filters['tutor__in'] = \
                Tutor.objects.filter(departments=req.department)
        else:
            filters['module__in'] = \
                Module.objects.filter(train_prog__department=req.department)
    else:
        scheds = ScheduledCourse.objects.filter(
            course__week=week,
            course__year=year,
            course__module__train_prog__department=req.department)\
                .prefetch_related('course__module__train_prog')

        if COSMO_MODE:
            filters['tutor__in'] = [sc.tutor for sc in scheds.distinct('tutor')]
        else:
            filters['module__in'] = [sc.course.module for sc in
                                     scheds.distinct('course__module')]
    
    dataset = Resource().export(Display.filter(**filters))
    return HttpResponse(dataset.csv, content_type='text/csv')

    
