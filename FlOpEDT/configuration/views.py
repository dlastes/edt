from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from django.db import transaction
from django.conf import settings

from django.contrib.admin.views.decorators import staff_member_required

from base.models import Department
from TTapp.scripts.TP_constraint import add_TP_constraints
from TTapp.scripts.DA_constraint import add_DA_limitedSlotChoices, add_DA_constraints
from TTapp.scripts.reasonableDays_constraint import add_reasonableDays_constraint

from .flush_database import flush_department_data, flush_planif_database
from misc.deploy_database.make_planif_file import make_planif_file
from .file_manipulation import upload_file, check_ext_file
from misc.deploy_database.extract_planif_file import extract_planif
from misc.deploy_database.deploy_database import extract_database_file
from misc.generate_static_files import generate_group_file, generate_room_file
from .forms import ImportPlanif, ImportConfig
from .models import UpdateConfig

import os
import datetime
import json


# Create your views here.


# @user_passes_test(check_admin)
# @login_required
@staff_member_required
def configuration(req, **kwargs):
    """
    Main view of Configuration
    :param req:
    :return:
    """
    arg_req = {}

    arg_req['form_config_1'] = ImportConfig()
    arg_req['form_config_2'] = ImportPlanif()

    up = UpdateConfig.objects.all()
    if up.count() > 0:
        arg_req['step'] = 2
    else:
        arg_req['step'] = 1
    # arg_req['departements'] = [tuple([depart.name, depart.abbrev]) for depart in Department.objects.all()]
    arg_req['departements'] = [{'name': depart.name, 'abbrev': depart.abbrev}
                               for depart in Department.objects.all() if not depart.abbrev == 'default']
    return render(req, 'configuration/configuration.html', arg_req)


# @ajax(login_required=True, is_superuser=True, require_POST=True)
@staff_member_required
def import_config_file(req, **kwargs):
    """
    View for the first step of the configuration. It imports the file
    to build the database, clear the database, extract the file to
    build the database and make the planif file for the second step
    of the configuration.
    Ajax request.

    :param req:
    :return:
    """
    if req.method == 'POST':
        form = ImportConfig(req.POST, req.FILES)
        print(req)
        print(req.FILES)
        if form.is_valid():
            print(req.FILES['fichier'])
            print(req.FILES['fichier'].name)
            if check_ext_file(req.FILES['fichier'], ['.xlsx', '.xls']):
                path = upload_file(req.FILES['fichier'], "configuration/database_file_.xlsx")
                # If one of method fail the transaction will be not commit.
                try:
                    with transaction.atomic():
                        depart_abbrev = req.POST['abbrev']
                        try:
                            depart_name = req.POST['nom']
                        except:
                            depart_name = None
                        print(depart_name)
                        try:
                            depart = Department.objects.get(abbrev=depart_abbrev)
                            if not depart_name == depart.name and depart_name is not None:
                                response = {'status': 'error', 'data': "Le département existe déja avec cette "
                                                                       "abrevviation et le nom ne correspond pas."}
                                return HttpResponse(json.dumps(response), content_type='application/json')
                            depart_name = depart.name
                            flush_department_data(depart)
                            print("flush OK")
                        except Exception:
                            pass


                        extract_database_file(path, department_name=depart_name,
                                              department_abbrev=depart_abbrev,
                                              )
                        print("extract OK")

                        update_version = UpdateConfig(date=datetime.datetime.now(), is_planif_update=False)
                        update_version.save()
                        print("create UpdateConfig OK")

                        os.rename(path, f"{settings.MEDIA_ROOT}/configuration/database_file_{depart_abbrev}.xlsx")
                        response = {'status': 'ok', 'data': 'OK'}
                except Exception as e:
                    os.remove(path)
                    print(e)
                    response = {'status': 'error', 'data': str(e)}
                    return HttpResponse(json.dumps(response), content_type='application/json')
                depart = Department.objects.get(abbrev=depart_abbrev)
                source = f"{settings.MEDIA_ROOT}/configuration/base/empty_planif_file.xlsx"
                target_repo = f"{settings.MEDIA_ROOT}/configuration/"
                make_planif_file(depart, empty_bookname=source, target_repo=target_repo)
                print("make planif OK")
            else:
                response = {'status': 'error', 'data': 'Invalid format'}
        else:
            response = {'status': 'error', 'data': 'Form not valid'}
    return HttpResponse(json.dumps(response), content_type='application/json')


# @user_passes_test(check_admin)
# @login_required
@staff_member_required
def get_config_file(req, **kwargs):
    """
    Resend the empty configuration's file.

    :param req:
    :return:
    """
    f = open(f"{settings.MEDIA_ROOT}/configuration/base/database_file.xlsx", "rb")
    response = HttpResponse(f, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="database_file.xls"'
    f.close()
    return response


# @user_passes_test(check_admin)
# @login_required
@staff_member_required
def get_planif_file(req, **kwargs):
    """
    Resend the empty planification's file. Only if the first step of
    the configuration has been done. This verification is done throught
    the existance of an object UpdateConfig in the database or the existance
    of the file which is to send (planif_file.xlsx).

    :param req:
    :return:
    """
    print(req.GET['departement'])
    up = UpdateConfig.objects.all()
    if up.count() == 0 or not os.path.exists(f"{settings.MEDIA_ROOT}/configuration/planif_file_{req.GET['departement']}.xlsx"):
        return HttpResponseNotFound("Not found")
    f = open(f"{settings.MEDIA_ROOT}/configuration/planif_file_{req.GET['departement']}.xlsx", "rb")
    response = HttpResponse(f, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="planif_file.xlsx"'
    f.close()
    return response


# @ajax(login_required=True, require_POST=True, is_superuser=True)
@staff_member_required
def import_planif_file(req, **kwargs):
    """
    Import a planification's file filled. Before data processing, it must to
    check if the first step of te configuration is done. After, it must to
    flush data related with the planification. Extract the data of the xlsx file
    and create constraints for the solver. (LimitedSlotChoices, SimultaneousCourse
    for TP and DA)
    Ajax request.

    :param req:
    :return:
    """
    up = UpdateConfig.objects.all()
    if up.count() == 0:
        return HttpResponse("The first step is missing")
    form = ImportPlanif(req.POST, req.FILES)
    if form.is_valid():
        if check_ext_file(req.FILES['fichier'], ['.xlsx', '.xls']):
            print(req.FILES['fichier'])
            path = upload_file(req.FILES['fichier'], "configuration/planif_file_.xlsx")
            # If one of methods fail, the transaction will be not commit.
            try:
                with transaction.atomic():
                    try:
                        depart = Department.objects.get(abbrev=req.POST['departement'])
                    except Exception as e:
                        response = {'status': 'error', 'data': str(e)}
                        return HttpResponse(json.dumps(response), content_type='application/json')
                    if len(up.filter(is_planif_update=True)) > 0:
                        flush_planif_database(depart)
                    print("Flush planif database OK")

                    extract_planif(depart, bookname=path)
                    print("Extract file OK")
                    rep = ""
                    add_DA_limitedSlotChoices()
                    add_DA_constraints(depart)
                    print("DA Constraint OK")

                    rep = add_TP_constraints(depart)
                    print("TP Constraint OK")

                    generate_group_file(depart.abbrev)
                    generate_room_file(depart.abbrev)
                    print("Generation des fichiers static")

                    # add_reasonableDays_constraint()
                    # print("Add Reasonable Days Constraint OK")

                    os.rename(path, f"{settings.MEDIA_ROOT}/configuration/planif_file.xlsx")
                    print("Rename OK")

                    update_version = UpdateConfig(date=datetime.datetime.now(), is_planif_update=True)
                    update_version.save()
                    print("Creation UpdateConfig OK")

                    response = {'status': 'ok', 'data': rep}
            except Exception as e:
                os.remove(path)
                print(e)
                response = {'status': 'error', 'data': str(e)}
        else:
            response = {'status': 'error', 'data': 'Invalid format'}
    else:
        response = {'status': 'error', 'data': 'Form can\'t be valid'}
    return HttpResponse(json.dumps(response), content_type='application/json')
