"""
Author : s.aryani456@gmail.com
Views related to gender
"""


# import libraries
from flask import request, Blueprint

# local imports
from constants.route_constants import GET_GENDER, ADD_GENDER, UPDATE_GENDER, DELETE_GENDER
from constants.flask_constants import GET, PUT, POST, DELETE
from constants import general_constants as gc
from codes.status_codes import OK, BAD_REQUEST, CREATED
from codes.response_codes import SUCCESS, FAIL
from helper.authorization import authorize_request
from helper.gender import get_all_genders, add_new_gender, update_gender, delete_gender
from helper.request_response import make_general_response, requires

gender_api = Blueprint("gender_api", __name__, url_prefix='')


@gender_api.route(GET_GENDER, methods=[GET])
@authorize_request
def get_genders():
    gender = get_all_genders()
    if gender:
        response = make_general_response(SUCCESS, "Success")
        response[gc.DATA] = gender
        return response, OK
    else:
        response = make_general_response(FAIL, "FAIL")
        return response, BAD_REQUEST


@gender_api.route(ADD_GENDER, methods=[POST])
@authorize_request
@requires([gc.GENDER], body=gc.JSON)
def add_genders():
    request_body = request.get_json()
    data, response_code, detail = add_new_gender(request_body[gc.GENDER])
    response = make_general_response(response_code, detail)
    if data:
        response[gc.DATA] = data
        return response, CREATED
    return response, BAD_REQUEST


@gender_api.route(UPDATE_GENDER, methods=[PUT])
@authorize_request
@requires([gc.ID, gc.GENDER], body=gc.JSON)
def update_genders():
    request_body = request.get_json()
    data, response_code, detail = update_gender(request_body[gc.ID], request_body[gc.GENDER])
    response = make_general_response(response_code, detail)
    if data:
        response[gc.DATA] = data
        return response, OK
    return response, BAD_REQUEST


@gender_api.route(DELETE_GENDER, methods=[DELETE])
@authorize_request
@requires([gc.ID], body=gc.QUERY_PARAMS)
def delete_genders():
    query_params = request.args
    deleted, code, detail = delete_gender(query_params[gc.ID])
    response = make_general_response(code, detail)
    response[gc.DELETED] = deleted
    if deleted:
        return response, OK
    return response, BAD_REQUEST
