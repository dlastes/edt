from django.shortcuts import render
from django.template.response import TemplateResponse

# Create your views here.
def manager(req, **kwargs):
    
    return TemplateResponse(req, 'cstmanager/index.html')