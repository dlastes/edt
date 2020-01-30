from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import user_passes_test
from base.models import Department
from flopeditor.check_tutor import check_tutor

@user_passes_test(check_tutor)
def home(request):
    return render(request, "flopeditor/home.html", {
        'departements': Department.objects.all(),
    })

@user_passes_test(check_tutor)
def department_parameters(request, department):
    return HttpResponse(department)
