import constants.general_constants as gc
import datetime
from flask import request
from codes.response_codes import PARAMETER_MISSING
from functools import wraps
from helper.validate import verify_param
from codes.status_codes import BAD_REQUEST


def request_header():
    return request.headers


def request_body():
    print("_____________", request)
    return request.get_json()


def requires(fields):
    def inner(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            body = request_body()

            print('fields_______________', fields)
            print('body_______________', body)
            missing = verify_param(fields, body)
            if missing:
                response = make_general_response(PARAMETER_MISSING, missing + " is missing")
                return response, BAD_REQUEST
            else:
                f(*args, **kwargs)

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
