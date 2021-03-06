from flask import request, Blueprint
from helper.authorization import authorize_request
from helper.request_response import *
from constants.route_constants import *
from constants.flask_constants import *
from codes.status_codes import *
from codes.response_codes import *
from helper.request_response import requires
from helper.madrassa_detail import set_new_madrassa_details, get_madrassa_detail_by_id
from common_apis.v1 import app

madrassa_detail_api = Blueprint("madrassa_detail_api", __name__, url_prefix='')


@madrassa_detail_api.route(SET_MADRASSA_DETAILS, methods=[POST])
@authorize_request
@requires([gc.MADRASSA_ID, gc.SHIFT_ID, gc.COURSE_ID], body=gc.JSON)
def set_madrassa_details():
    request_body = request.get_json()
    data, response_code, detail = set_new_madrassa_details(request_body[gc.SHIFT_ID], request_body[gc.COURSE_ID],
                                                           request_body[gc.MADRASSA_ID])
    response = make_general_response(response_code, detail)
    if data:
        print(f"_____________________{data}")
        response[gc.DATA] = data
        return response, CREATED
    return response, BAD_REQUEST


@madrassa_detail_api.route(GET_MADRASSA_DETAILS, methods=[GET])
@authorize_request
@requires([gc.MADRASSA_ID], body=gc.QUERY_PARAMS)
def get_madrassa_details():
    query_params = request.args
    madrassa_detail_id = query_params.get(gc.MADRASSA_ID)
    madrassa_detail = get_madrassa_detail_by_id(madrassa_detail_id)
    if madrassa_detail:
        response = make_general_response(SUCCESS, "Success")
        response[gc.DATA] = madrassa_detail
        return response, OK
    else:
        response = make_general_response(MADRASSA_NOT_FOUND, "Madrassa Details Not found")
        return response, BAD_REQUEST
