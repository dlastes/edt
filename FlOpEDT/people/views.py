# -*- coding: utf-8 -*-


from django.shortcuts import render
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.core.exceptions import ObjectDoesNotExist

import base.queries as queries

from people.models import Tutor, GroupPreferences, StudentPreferences, Student, NotificationsPreferences
from people.admin import TutorResource, GroupPreferencesResource, StudentPreferencesResource


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


@login_required
def student_preferences(req):
    if req.method=='POST' :
        print(req)
        if req.user.is_authenticated and req.user.is_student:
            user = req.user
            morning_weight = req.POST['morning_evening']
            free_half_day_weight = req.POST['light_free']

            student = Student.objects.get(username=user.username)
            student_pref, created = StudentPreferences.objects.get_or_create(student=student)
            if created:
                student_pref.save()
            student_pref.morning_weight = morning_weight
            student_pref.free_half_day_weight = free_half_day_weight
            student_pref.save()
            group_pref = None
            for group in student.belong_to.all() :
                group_pref, created = GroupPreferences.objects.get_or_create(group=group)
                if created:
                    group_pref.save()
            if group_pref is not None:
                group_pref.calculate_fields()
                group_pref.save()
            return redirect("base:edt", department=req.department)
        else:
            raise Http404("Who are you?")
    else:
        if req.user.is_authenticated and req.user.is_student:
            student = Student.objects.get(username=req.user.username)
            try:
                student_pref = StudentPreferences.objects.get(student=student)
            except ObjectDoesNotExist:
                student_pref = StudentPreferences(student=student)
                student_pref.save()
            morning = student_pref.morning_weight
            free_half_day = student_pref.free_half_day_weight
            return TemplateResponse(
                req,
                'people/studentPreferencesSelection.html',
                {'morning': morning,
                 'free_half_day': free_half_day,
                 'user_notifications_pref':
                 queries.get_notification_preference(req.user)
                })
        else:
            # Make a decorator instead
            raise Http404("Who are you?")
        


def create_user(req):
    print(req.user)
    print(req.user.is_authenticated and req.user.has_department_perm(req.department))
    return TemplateResponse(req, 'people/login_create.html')
