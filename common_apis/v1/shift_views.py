from flask import request, Blueprint
from helper.authorization import authorize_request
from helper.request_response import *
from helper.validate import *
from helper.database import *
from config.db_column_to_response import mapper
from constants.route_constants import *
from constants.flask_constants import *
from constants.table_names import *
from constants.column_names import *
from database_layer.database import select_query, insert_query
from codes.status_codes import *
from codes.response_codes import *
from common_apis.v1 import app

shift_api = Blueprint("shift_api", __name__, url_prefix='')


@shift_api.route(GET_SHIFTS, methods=[GET])
@authorize_request
def get_shifts():
    query = f"select * from {SHIFT}"
    r = select_query(query)
    result = r.fetchall()
    data = []
    for i in result:
        mapped_data = map_response(i, mapper)
        print(mapped_data)
        data.append(mapped_data)
    response = make_general_response(SUCCESS, "Success")
    response[gc.DATA] = data
    return response, OK


@shift_api.route(ADD_SHIFT, methods=[POST])
@authorize_request
def add_shifts():
    request_body = request.get_json()
    missing = verify_param([gc.NAME, gc.START_TIME, gc.END_TIME], request_body)
    if missing:
        response = make_general_response(PARAMETER_MISSING, missing + " is missing")
        return response, BAD_REQUEST

    flag, start_time = validate_time(request_body[gc.START_TIME])
    if not flag:
        response = make_general_response(INVALID_PARAMETER, "Invalid Start Time format allowed is hhmm")
        return response, BAD_REQUEST

    flag, end_time = validate_time(request_body[gc.END_TIME])
    if not flag:
        response = make_general_response(INVALID_PARAMETER, "Invalid End Time format allowed is hhmm")
        return response, BAD_REQUEST

    index = select_max(SHIFT) + 1

    query = f"insert into shift(id,shift_name,start_time,end_time) " \
            f"values({index},'{request_body[gc.NAME]}','{start_time}','{end_time}')"
    r = insert_query(query)
    if r:
        query = f"select * from {SHIFT} where {ID} = {index}"
        r = select_query(query)
        result = r.fetchall()
        for i in result:
            data = map_response(i, mapper)

        response = make_general_response(SUCCESS, "SUCCESS")
        response[gc.DATA] = data
        return response, CREATED

    else:
        response = make_general_response(FAIL, "FAIL")
        return response, OK


@shift_api.route(UPDATE_SHIFT, methods=[PUT])
@authorize_request
def update_shifts():
    request_body = request.get_json()
    missing = verify_param([gc.ID, gc.NAME, gc.START_TIME, gc.END_TIME], request_body)
    if missing:
        response = make_general_response(PARAMETER_MISSING, missing + " is missing")
        return response, BAD_REQUEST

    flag, start_time = validate_time(request_body[gc.START_TIME])
    if not flag:
        response = make_general_response(INVALID_PARAMETER, "Invalid Start Time format allowed is hhmm")
        return response, BAD_REQUEST

    flag, end_time = validate_time(request_body[gc.END_TIME])
    if not flag:
        response = make_general_response(INVALID_PARAMETER, "Invalid End Time format allowed is hhmm")
        return response, BAD_REQUEST

    query = f"update {SHIFT}" \
            f" set {SHIFT_NAME} = '{request_body[gc.NAME]}' , {START_TIME} = '{start_time}', " \
            f"{END_TIME}= '{end_time}' where {ID} = {request_body[gc.ID]}"
    r = insert_query(query)
    if r:
        query = f"select * from {SHIFT} where {ID} = {request_body[gc.ID]}"
        r = select_query(query)
        result = r.fetchall()
        for i in result:
            data = map_response(i, mapper)

        response = make_general_response(SUCCESS, "SUCCESS")
        response[gc.DATA] = data
        return response, CREATED

    else:
        response = make_general_response(SHIFT_NOT_FOUND, "ShiftID not found or Already Updated")
        return response, OK


@shift_api.route(DELETE_SHIFTS, methods=[DELETE])
@authorize_request
def delete_shifts():
    query_params = request.args
    length_query_param = len(query_params)
    if length_query_param == 0:
        response = make_general_response(MISSING_QUERY_PARAM, "Query params are missing")
        return response, BAD_REQUEST

    elif len(query_params) > 1:
        response = make_general_response(ADDITIONAL_QUERY_PARAM, "Additional Query params")
        return response, BAD_REQUEST

    elif not query_params.get(ID):
        response = make_general_response(INVALID_QUERY_PARAM, "Invalid query params")
        return response, BAD_REQUEST

    query = f"select * from {MADRASSA_DETAILS} where {SHIFT_ID}={query_params[gc.ID]}"
    r = select_query(query)
    result = r.fetchall()
    if len(result) > 0:
        response = make_general_response(SHIFT_NOT_FOUND, f"Cannot delete shiftID {query_params[gc.ID]}."
                                                          f"It is in used somewhere else")
        return response, OK

    query = f'delete from {SHIFT} where {ID}={query_params[gc.ID]}'
    r = insert_query(query)
    if r:
        response = make_general_response(SUCCESS, "SUCCESS")
        response[gc.DELETED] = r
        return response, CREATED

    else:
        response = make_general_response(SHIFT_NOT_FOUND, "ShiftID not found")
        response[gc.DELETED] = r
        return response, OK
