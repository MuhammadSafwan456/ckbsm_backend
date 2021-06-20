"""
Author : s.aryani456@gmail.com
Views related to madrassa details
"""


# import libraries
from flask import request, Blueprint

# local imports
from constants.route_constants import SET_MADRASSA_DETAILS, GET_MADRASSA_DETAILS
from constants.flask_constants import GET, POST
from constants import general_constants as gc
from codes.status_codes import OK, BAD_REQUEST, CREATED
from codes.response_codes import SUCCESS, MADRASSA_DETAILS_NOT_FOUND
from helper.authorization import authorize_request
from helper.madrassa_detail import set_new_madrassa_details, get_madrassa_detail_by_id
from helper.request_response import make_general_response, requires

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
        response = make_general_response(MADRASSA_DETAILS_NOT_FOUND, "Madrassa Details Not found")
        return response, BAD_REQUEST
