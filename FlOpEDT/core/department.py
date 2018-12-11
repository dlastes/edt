from base.models import Department, CourseType, TrainingProgramme, Module, Group
from people.models import Tutor, FullStaff

def get_department_lookup(field, department, include_field_name=True):
    # Get filter to apply for department filtering 
    # of model instances depending on their fields 
    if not field.auto_created and field.related_model:
        lookups_by_model = {
            Department: '',
            FullStaff: '',
            CourseType: 'department',
            TrainingProgramme: 'department',
            Module: 'train_prog__department',
            Tutor: 'departments',
            Group: 'train_prog__department',
            }
        
        lookup = lookups_by_model.get(field.related_model, None)

        if not lookup is None:
            if lookup is '':
                lookup_name = field.name
            elif include_field_name:
                lookup_name = f"{field.name}__{lookup}"
            else:
                lookup_name = lookup

            return {lookup_name: department}

    return None  