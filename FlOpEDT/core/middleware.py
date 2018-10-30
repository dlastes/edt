import logging

from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist

from base.models import Department

class EdtContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):

        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if 'department' in view_kwargs:
            department = view_kwargs['department']
            try:                
                request.department = Department.objects.get(abbrev=department)
            except ObjectDoesNotExist:
                return redirect('/')

    def process_template_response(self, request, response):
        if hasattr(request, 'department'):
            response.context_data['department'] = request.department.abbrev

        return response