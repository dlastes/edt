# -*- coding: utf-8 -*-


from django.shortcuts import render
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import Tutor, GroupPreferences, StudentPreferences
from .admin import TutorResource
from django.template.response import TemplateResponse
import base


def redirect_add_people_kind(req, kind):
    if kind == "stud":
        return redirect('people:add_student')
    elif kind == "full":
        return redirect('people:add_fullstaff')
    elif kind == "supp":
        return redirect('people:add_supplystaff')
    elif kind == "BIAT":
        return redirect('people:add_BIATOS')
    else:
        raise Http404("I don't know this kind of people.")


@login_required
def redirect_change_people_kind(req):
    if req.user.is_student:
        return redirect('people:change_student')
    if req.user.is_tutor:
        if req.user.tutor.status == Tutor.FULL_STAFF:
            return redirect('people:change_fullstaff')
        if req.user.tutor.status == Tutor.SUPP_STAFF:
            return redirect('people:change_supplystaff')
        if req.user.tutor.status == Tutor.BIATOS:
            return redirect('people:change_BIATOS')
    else:
        raise Http404("Who are you?")


def fetch_tutors(req):
	dataset = TutorResource().export(Tutor.objects.all())
	response = HttpResponse(dataset.csv,
                                content_type='text/csv')
	return response

def student_preferences(req):
    if req.method=='POST' :
        if req.user.is_authenticated and req.user.is_student:
            user = req.user
            morning_weight = req.POST['morning_weight']
            morning_weight = req.POST['free_half_day_weight']

            student = Student.objects.filter(username=user.username)
            student_preferences = StudentPreferences.objects.filter(student__username=student.username)
            student_preferences.morning_weight = morning_weight
            student_preferences.free_half_day_weight = free_half_day_weight
            student_preferences.save()
            group_preferences = GroupPreferences.objects.filter(group__nom=student.belong_to)
            group_preferences.calculate_fields()
            group_preferences.save()
            return redirect('base:edt')
        else :
            raise Http404("Who are you?")
    else :
        return TemplateResponse(req, 'people/studentPreferencesSelection.html', {})
