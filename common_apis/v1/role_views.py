from flask import request,Blueprint
from helper.authorization import authorize_request
from helper.response import *
from helper.validate import *
from helper.database import *
from config.db_column_to_response import mapper
from constants.route_constants import *
from constants.flask_constants import *
from constants.table_names import *
from constants.column_names import *
from database_layer.database import select_query,insert_query
from codes.status_codes import *
from codes.response_codes import *
from common_apis.v1 import app

role_api = Blueprint("role_api", __name__, url_prefix='')


@role_api.route(GET_ROLES, methods=[GET])
@authorize_request
def get_roles():
    query = f"select * from {ROLE}"
    r = select_query(query)
    result = r.fetchall()
    data = []
    for i in result:
        mapped_data = map_response(i, mapper)
        data.append(mapped_data)
    response = make_general_response(SUCCESS, "Success")
    response[gc.DATA] = data
    return response, OK


@role_api.route(ADD_ROLES, methods=[POST])
@authorize_request
def add_roles():
    request_body = request.get_json()
    missing = verify_param([gc.NAME], request_body)
    if missing:
        response = make_general_response(PARAMETER_MISSING, missing + " is missing")
        return response, BAD_REQUEST
    index = select_max(ROLE) + 1

    query = f"insert into {ROLE}({ID}, {ROLE_NAME}) values({index},'{request_body[gc.NAME]}')"
    r = insert_query(query)
    if r:
        query = f"select * from {ROLE} where id = {index}"
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


@role_api.route(UPDATE_ROLES, methods=[PUT])
@authorize_request
def update_roles():
    request_body = request.get_json()
    missing = verify_param([gc.ID, gc.NAME], request_body)
    if missing:
        response = make_general_response(PARAMETER_MISSING, missing + " is missing")
        return response, BAD_REQUEST

    query = f"update {ROLE} set {ROLE_NAME} = '{request_body[gc.NAME]}' where id = {request_body[gc.ID]}"
    r = insert_query(query)
    if r:
        query = f"select * from {ROLE} where {ID} = {request_body[gc.ID]}"
        r = select_query(query)
        result = r.fetchall()
        for i in result:
            data = map_response(i, mapper)

        response = make_general_response(SUCCESS, "SUCCESS")
        response[gc.DATA] = data
        return response, CREATED

    else:
        response = make_general_response(ROLE_NOT_FOUND, "RoleID not found or Already Updated")
        return response, OK


@role_api.route(DELETE_ROLES, methods=[DELETE])
@authorize_request
def delete_roles():
    query_params = request.args
    length_query_param = len(query_params)
    if length_query_param == 0:
        response = make_general_response(MISSING_QUERY_PARAM, "Query params are missing")
        return response, BAD_REQUEST

    elif len(query_params) > 1:
        response = make_general_response(ADDITIONAL_QUERY_PARAM, "Additional Query params")
        return response, BAD_REQUEST

    elif not query_params.get(gc.ID):
        response = make_general_response(INVALID_QUERY_PARAM, "Invalid query params")
        return response, BAD_REQUEST

    query = f"select * from {ENROLLMENT} where {ROLE_ID}={query_params[gc.ID]}"
    r = select_query(query)
    result = r.fetchall()
    if len(result) > 0:
        response = make_general_response(SHIFT_NOT_FOUND,
                                         f"Cannot delete roleID {query_params[gc.ID]}.It is in used somewhere else")
        return response, OK
    query = f'delete from {ROLE} where {ID} ={query_params[gc.ID]}'
    r = insert_query(query)
    if r:
        response = make_general_response(SUCCESS, "SUCCESS")
        response[gc.DELETED] = r
        return response, CREATED

    else:
        response = make_general_response(ROLE_NOT_FOUND, "RoleID not found")
        response[gc.DELETED] = r
        return response, OK
