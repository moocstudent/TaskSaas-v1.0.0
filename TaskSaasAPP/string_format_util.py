import re


def format_error_msg(dict_errors):
    error_msg = ''
    for i in dict_errors.values():
        error_msg += i[0] + ','
    error_msg = error_msg[:-1]
    return error_msg

