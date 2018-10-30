from django.conf import settings


def edt_context(request):
    print("---------------" + str(request))
    if hasattr(request, 'department'):
        print("------------ssssss---" + str(request))
        return {'department': request.department.abbrev}
    else:
        return {}