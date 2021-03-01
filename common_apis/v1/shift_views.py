from flask import request, Blueprint
from helper.authorization import authorize_request
from helper.request_response import *
from helper.validate import *
from helper.database import *
from config.db_column_to_response import mapper
from constants.route_constants import *
from constants.flask_constants import *
from codes.status_codes import *
from codes.response_codes import *
from helper.shift import get_all_shifts, add_new_shift, update_shift, delete_shift
from common_apis.v1 import app
from helper.request_response import requires

shift_api = Blueprint("shift_api", __name__, url_prefix='')


@shift_api.route(GET_SHIFTS, methods=[GET])
@authorize_request
def get_shifts():
    shifts = get_all_shifts()
    if shifts:
        response = make_general_response(SUCCESS, "Success")
        response[gc.DATA] = shifts
        return response, OK
    else:
        response = make_general_response(FAIL, "FAIL")
        return response, BAD_REQUEST


@shift_api.route(ADD_SHIFT, methods=[POST])
@authorize_request
@requires([gc.NAME, gc.START_TIME, gc.END_TIME], body=gc.JSON)
def add_shifts():
    request_body = request.get_json()

    flag, start_time = validate_time(request_body[gc.START_TIME])
    if not flag:
        response = make_general_response(INVALID_PARAMETER, "Invalid Start Time format allowed is hhmm")
        return response, BAD_REQUEST

    flag, end_time = validate_time(request_body[gc.END_TIME])
    if not flag:
        response = make_general_response(INVALID_PARAMETER, "Invalid End Time format allowed is hhmm")
        return response, BAD_REQUEST

    data, response_code, detail = add_new_shift(request_body[gc.NAME], start_time, end_time)
    response = make_general_response(response_code, detail)
    if data:
        response[gc.DATA] = data
        return response, CREATED
    return response, BAD_REQUEST


@shift_api.route(UPDATE_SHIFT, methods=[PUT])
@authorize_request
@requires([gc.NAME, gc.START_TIME, gc.END_TIME], body=gc.JSON)
def update_shifts():
    request_body = request.get_json()

    flag, start_time = validate_time(request_body[gc.START_TIME])
    if not flag:
        response = make_general_response(INVALID_PARAMETER, "Invalid Start Time format allowed is hhmm")
        return response, BAD_REQUEST

    flag, end_time = validate_time(request_body[gc.END_TIME])
    if not flag:
        response = make_general_response(INVALID_PARAMETER, "Invalid End Time format allowed is hhmm")
        return response, BAD_REQUEST

    data, response_code, detail = update_shift(request_body[gc.ID], request_body[gc.NAME], start_time, end_time)
    response = make_general_response(response_code, detail)
    if data:
        response[gc.DATA] = data
        return response, OK
    return response, BAD_REQUEST





@shift_api.route(DELETE_SHIFTS, methods=[DELETE])
@authorize_request
@requires([gc.ID], body=gc.QUERY_PARAMS)
def delete_shifts():
    query_params = request.args
    deleted, code, detail = delete_shift(query_params[gc.ID])
    response = make_general_response(code, detail)
    response[gc.DELETED] = deleted
    if deleted:
        return response, OK
    return response, BAD_REQUEST

