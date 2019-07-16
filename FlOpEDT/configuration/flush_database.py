from django.apps import apps
from people.models import User
from base.models import Course


def flush_department_data(departement):
    """
    Delete all object in the database except superusers.
    :return:
    """
    departement.delete()


def flush_planif_database(departement):
    Course.objects.filter(groupe__train_prog__department=departement).delete()
