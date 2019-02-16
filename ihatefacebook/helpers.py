from os.path import isfile, isdir, getsize
from os import mkdir
import sys
import json


def cmk_dir(directory):
    """
    (Check & make dir) Create the directory if it doesn't exist. Terminates the script after giving an error message
    if an exception happens.

    :param directory: The directory to be checked.
    :param force_owner: Sets the owner of the file to be the current user. This is useful where default mode (0o777) is
    ignored by Python. See mkdir reference.
    """
    if not isdir(directory):
        try:
            mkdir(directory)
        except Exception as ex:
            print("ERROR: %s" % ex)
            sys.exit(1)


def read_json(file_path):
    """
    Read JSON from file.

    :param file_path: path of the file to be read.
    :return:
        list or dictionary of extracted JSON - if the files is found
        False - if the file isn't found OR it's empty
    :raises:
        Whatever exception json.load() may raise.
    """
    if isfile(file_path):
        if getsize(file_path) == 0:
            return False
        with open(file_path) as file:
            file.seek(0)
            data = json.load(file)
            return data if len(data) > 0 else False
    else:
        return False


def get_complement_items(list_a, list_b):
    """
    Performs B - A. Extracts the relative complement (set difference) events of two lists, i.e. items that
    are in the first list but not in the second.

    :param list_a: First list.
    :param list_b: Second list.
    :return: set_difference_events: A list of the resulting items.
    """
    list_set_difference = list()
    for item in list_b:
        if item not in list_a:
            list_set_difference.append(item)
    return list_set_difference
