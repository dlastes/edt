from datetime import datetime
from django.http import JsonResponse
from django.template.response import TemplateResponse 
from base.core.statistics import get_room_activity_by_day

#@login_required
def fetch_room_activity(req, **kwargs):
    current_year = datetime.now().year
    return JsonResponse(get_room_activity_by_day(req.department, current_year))

#@login_required
def index(req, **kwargs):
    return TemplateResponse(req, 'base/statistics.html')
