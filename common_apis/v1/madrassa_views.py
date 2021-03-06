from flask import request, Blueprint
from helper.authorization import authorize_request
from helper.request_response import *
from helper.validate import *
from constants.route_constants import *
from constants.flask_constants import *
from codes.status_codes import *
from codes.response_codes import *
from helper.madrassa import get_all_madrassas, add_new_madrassa, update_madrassa, delete_madrassa
from common_apis.v1 import app
from helper.request_response import requires

madrassa_api = Blueprint("madrassa_api", __name__, url_prefix='')


@madrassa_api.route(GET_MADRASSAS, methods=[GET])
@authorize_request
def get_madrassas():
    madrassas = get_all_madrassas()
    if madrassas:
        response = make_general_response(SUCCESS, "Success")
        response[gc.DATA] = madrassas
        return response, OK
    else:
        response = make_general_response(FAIL, "FAIL")
        return response, BAD_REQUEST


@madrassa_api.route(ADD_MADRASSAS, methods=[POST])
@authorize_request
@requires([gc.NAME], body=gc.JSON)
def add_madrassas():
    request_body = request.get_json()
    data, response_code, detail = add_new_madrassa(request_body[gc.NAME])
    response = make_general_response(response_code, detail)
    if data:
        response[gc.DATA] = data
        return response, CREATED
    return response, BAD_REQUEST


@madrassa_api.route(UPDATE_MADRASSAS, methods=[PUT])
@authorize_request
@requires([gc.ID, gc.NAME], body=gc.JSON)
def update_madrassas():
    request_body = request.get_json()
    data, response_code, detail = update_madrassa(request_body[gc.ID], request_body[gc.NAME])
    response = make_general_response(response_code, detail)
    if data:
        response[gc.DATA] = data
        return response, OK
    return response, BAD_REQUEST


@madrassa_api.route(DELETE_MADRASSAS, methods=[DELETE])
@authorize_request
@requires([gc.ID], body=gc.QUERY_PARAMS)
def delete_madrassas():
    query_params = request.args
    deleted, code, detail = delete_madrassa(query_params[gc.ID])
    response = make_general_response(code, detail)
    response[gc.DELETED] = deleted
    if deleted:
        return response, OK
    return response, BAD_REQUEST

