"""
Author : s.aryani456@gmail.com
helper functions related to incoming request and outgoing response
"""


from functools import wraps
import datetime
from flask import request

from codes.response_codes import PARAMETER_MISSING, FAIL
from codes.status_codes import BAD_REQUEST
from constants import general_constants as gc
from helper.validate import verify_param


def request_header():
    return request.headers


def requires(fields, **agr):
    def inner(f):
        @wraps(f)
        def wrap(*args, **kwargs):

            if agr.get(gc.BODY) == gc.JSON:
                body = request.get_json()
            elif agr.get(gc.BODY) == gc.QUERY_PARAMS:
                body = request.args
            else:
                response = make_general_response(FAIL, "FAIL")
                return response, BAD_REQUEST

            missing = verify_param(fields, body)
            if missing:
                response = make_general_response(PARAMETER_MISSING, missing + " is missing")
                return response, BAD_REQUEST
            else:
                return f(*args, **kwargs)

        return wrap

    return inner


def make_general_response(code, detail):
    response = {
        gc.RESPONSE_CODE: code,
        gc.RESPONSE_DETAIL: detail
    }
    return response


def make_missing_parameter_response(parameter):
    response = {
        gc.RESPONSE_CODE: PARAMETER_MISSING,
        gc.RESPONSE_DETAIL: parameter + " is missing"
    }
    return response


def map_response(original_dict, mapper):
    data = {}
    for key in original_dict:
        if isinstance(original_dict[key], datetime.timedelta):
            data[mapper[key]] = str(original_dict[key])
        else:
            data[mapper[key]] = original_dict[key]
    return data
