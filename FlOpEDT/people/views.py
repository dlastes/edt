# -*- coding: utf-8 -*-


from django.shortcuts import render
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import Tutor, GroupPreferences, StudentPreferences, Student
from .admin import TutorResource, GroupPreferencesResource, StudentPreferencesResource
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


def fetch_preferences_group(req):
    dataset = GroupPreferencesResource().export(GroupPreferences.objects.all())
    response = HttpResponse(dataset.csv,
                                content_type='text/csv')
    return response


def fetch_preferences_students(req):
    dataset = StudentPreferencesResource().export(StudentPreferences.objects.all())
    response = HttpResponse(dataset.csv,
                                content_type='text/csv')
    return response


def student_preferences(req):
    if req.method=='POST' :
        print(req)
        if req.user.is_authenticated and req.user.is_student:
            user = req.user
            morning_weight = req.POST['morning_evening']
            free_half_day_weight = req.POST['light_free']

            student = Student.objects.get(username=user.username)
            student_preferences, created = StudentPreferences.objects.get_or_create(student=student)
            if created:
                student_preferences.save()
            student_preferences.morning_weight = morning_weight
            student_preferences.free_half_day_weight = free_half_day_weight
            student_preferences.save()
            for group in student.belong_to.all() :
                group_preferences = GroupPreferences.objects.get(group=group)
                group_preferences.save()
            group_preferences.calculate_fields()
            group_preferences.save()
            return redirect("base.index")
        else:
            raise Http404("Who are you?")
    else:
        return TemplateResponse(req, 'people/studentPreferencesSelection.html', {})
