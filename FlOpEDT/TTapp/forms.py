from django import forms
from base.models import Department
from base.models import Course

class DepartmentForm(forms.Form):
    a = []
    for i in Department.objects.all():
        a.append((i.name, i.abbrev))
    department = forms.ChoiceField(choices=a)

class IntForm(forms.Form):
    week = forms.IntegerField()
