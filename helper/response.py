import constants.general_constants as gc
import datetime
from codes.response_codes import PARAMETER_MISSING


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
