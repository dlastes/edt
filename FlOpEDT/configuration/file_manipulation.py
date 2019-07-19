from django.conf import settings
import os

def upload_file(file, file_name):
    """
    Save the file at the path in the folder MEDIA.
    :param file: the file
    :param path_name: the target's path
    :return: the path of the saved file
    """
    path = os.path.join(settings.MEDIA_ROOT, file_name)
    with open(path, 'wb+') as dest:
        for chunk in file.chunks():
            dest.write(chunk)
    return path


def check_ext_file(file, exts):
    """
    Check the matching of extension file.
    :param file: file name
    :param exts: extensions to match against
    :return:
    """
    for ext in exts:
        if file.name.endswith(ext):
            return True
    return False
