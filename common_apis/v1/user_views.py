from flask import Blueprint
from helper.authorization import authorize_request
from helper.request_response import *
from helper.validate import *
from constants.route_constants import *
from constants.flask_constants import *
from constants.column_names import *
from codes.status_codes import *
from codes.response_codes import *
from helper.user import find_user_by_id, enroll_user_in_madrassa
from helper.madrassa_detail import find_madrassa_detail_by_id
from helper.role import find_role_by_id
from helper.request_response import requires
from helper.user import add_new_user, find_user_by_cnic_or_contact

user_api = Blueprint("user_api", __name__, url_prefix='')


@user_api.route(ADD_USER, methods=[POST])
@authorize_request
@requires([gc.NAME, gc.FATHER_NAME, gc.CNIC, gc.EMAIL, gc.MOTHER_TONGUE, gc.CONTACT, gc.GENDER_ID, gc.GUARDIAN_NAME,
           gc.GUARDIAN_CONTACT, gc.DATE_OF_BIRTH, gc.AGE], body=gc.JSON)
def add_user():
    request_body = request.get_json()

    if not validate_cnic(request_body.get(gc.CNIC)):
        response = make_general_response(INVALID_PARAMETER, "Invalid CNIC")
        return response, BAD_REQUEST

    if not validate_email(request_body.get(gc.EMAIL)):
        response = make_general_response(INVALID_PARAMETER, "Invalid Email ID")
        return response, BAD_REQUEST

    if not validate_contact(request_body.get(gc.CONTACT)):
        response = make_general_response(INVALID_PARAMETER, "Invalid Contact")
        return response, BAD_REQUEST

    if not validate_contact(request_body.get(gc.GUARDIAN_CONTACT)):
        response = make_general_response(INVALID_PARAMETER, "Invalid Guardian Contact")
        return response, BAD_REQUEST

    if not validate_date(request_body.get(gc.DATE_OF_BIRTH)):
        response = make_general_response(INVALID_PARAMETER, "Invalid DOB. Allowed Date format is YYYYMMDD")
        return response, BAD_REQUEST

    user_param = request_body

    data, response_code, detail = add_new_user(user_param)
    response = make_general_response(response_code, detail)
    if data:
        response[gc.DATA] = data
        return response, CREATED
    return response, BAD_REQUEST


@user_api.route(GET_USERS, methods=[GET])
@authorize_request
def get_users():
    query_params = request.args
    if not query_params.get(CNIC) and not query_params.get(CONTACT):
        response = make_general_response(INVALID_QUERY_PARAM, "Invalid query params")
        return response, BAD_REQUEST

    cnic = query_params.get(CNIC)
    contact = query_params.get(CONTACT)

    if cnic and not validate_cnic(cnic):
        response = make_general_response(INVALID_PARAMETER, "Invalid CNIC")
        return response, BAD_REQUEST

    if contact and not validate_contact(contact):
        response = make_general_response(INVALID_PARAMETER, "Invalid contact")
        return response, BAD_REQUEST

    users = find_user_by_cnic_or_contact(cnic, contact)
    if users:
        response = make_general_response(SUCCESS, "Success")
        response[gc.DATA] = users
        return response, OK
    else:
        response = make_general_response(USER_NOT_FOUND, "User Not found")
        return response, BAD_REQUEST


@user_api.route(ENROLL_USER, methods=[POST])
@authorize_request
@requires([gc.USER_ID, gc.ENROLMENT_DATE, gc.MADRASSA_DETAIL, gc.ROLE_ID], body=gc.JSON)
def enroll_users():
    request_body = request.get_json()
    _id = request_body[gc.USER_ID]
    user = find_user_by_id(_id)

    if not user:
        response = make_general_response(USER_NOT_FOUND, "User not found")
        return response, BAD_REQUEST

    madrassa_detail_id = request_body[gc.MADRASSA_DETAIL]
    madrassa_detail = find_madrassa_detail_by_id(madrassa_detail_id)

    if not madrassa_detail:
        response = make_general_response(MADRASSA_DETAILS_NOT_FOUND, "Madrassa details not found")
        return response, BAD_REQUEST

    role_id = request_body[gc.ROLE_ID]
    role = find_role_by_id(role_id)

    if not role:
        response = make_general_response(ROLE_NOT_FOUND, "Role not found")
        return response, BAD_REQUEST

    enrollment_date = request_body[gc.ENROLMENT_DATE]
    if not validate_date(enrollment_date):
        response = make_general_response(INVALID_PARAMETER, "Invalid Date Format. Allowed Date format is YYYYMMDD")
        return response, BAD_REQUEST

    enrolled, response_code, detail = enroll_user_in_madrassa(user, madrassa_detail, role, enrollment_date)
    response = make_general_response(response_code, detail)
    if enrolled:
        return response, OK
    return response, BAD_REQUEST
