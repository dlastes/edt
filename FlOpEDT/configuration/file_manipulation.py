from django.conf import settings


def upload_file(file, path_name):
    """
    Save the file at the path in the folder MEDIA.
    :param file: the file
    :param path_name: the target's path
    :return: the path of the saved file
    """
    path = f"{settings.MEDIA_ROOT}/{path_name}"
    with open(path, 'wb+') as dest:
        for chunk in file.chunks():
            dest.write(chunk)
    return path


def check_ext_file(file, exts):
    """
    Check the matching of extension file.
    :param file:
    :param ext:
    :return:
    """
    for ext in exts:
        if file.name.endswith(ext):
            return True
    return False