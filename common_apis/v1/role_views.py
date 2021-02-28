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
from helper.role import add_new_role, get_all_roles, update_role
from helper.request_response import requires

role_api = Blueprint("role_api", __name__, url_prefix='')


@role_api.route(GET_ROLES, methods=[GET])
@authorize_request
def get_roles():
    roles = get_all_roles()
    if roles:
        response = make_general_response(SUCCESS, "Success")
        response[gc.DATA] = roles
        return response, OK
    else:
        response = make_general_response(FAIL, "FAIL")
        return response, BAD_REQUEST


@role_api.route(ADD_ROLES, methods=[POST])
@authorize_request
@requires([gc.NAME], body=gc.JSON)
def add_roles():
    request_body = request.get_json()
    data, response_code, detail = add_new_role(request_body[gc.NAME])
    response = make_general_response(response_code, detail)
    if data:
        response[gc.DATA] = data
        return response, CREATED
    return response, BAD_REQUEST


@role_api.route(UPDATE_ROLES, methods=[PUT])
@authorize_request
@requires([gc.ID, gc.NAME], body=gc.JSON)
def update_roles():
    request_body = request.get_json()
    data, response_code, detail = update_role(request_body[gc.ID], request_body[gc.NAME])
    response = make_general_response(response_code, detail)
    if data:
        response[gc.DATA] = data
        return response, OK
    return response, BAD_REQUEST


@role_api.route(DELETE_ROLES, methods=[DELETE])
@authorize_request
@requires([gc.ID], body=gc.QUERY_PARAMS)
def delete_roles():
    query_params = request.args

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
