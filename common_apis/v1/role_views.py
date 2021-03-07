# import libraries
from flask import request, Blueprint

# local imports
from constants.route_constants import GET_ROLES, ADD_ROLES, UPDATE_ROLES, DELETE_ROLES
from constants.flask_constants import GET, PUT, POST, DELETE
from constants import general_constants as gc
from codes.status_codes import OK, BAD_REQUEST, CREATED
from codes.response_codes import SUCCESS, FAIL
from helper.authorization import authorize_request
from helper.role import get_all_roles, add_new_role, update_role, delete_role
from helper.request_response import make_general_response, requires

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
    deleted, code, detail = delete_role(query_params[gc.ID])
    response = make_general_response(code,detail)
    response[gc.DELETED] = deleted
    if deleted:
        return response, OK
    return response, BAD_REQUEST


