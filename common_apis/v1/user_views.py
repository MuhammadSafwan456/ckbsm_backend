from flask import request, jsonify, Blueprint
from helper.authorization import authorize_request
from helper.response import *
from helper.validate import *
from helper.database import *
from constants.route_constants import *
from constants.flask_constants import *
from constants.table_names import *
from constants.column_names import *
from database_layer.database import select_query, insert_query
from codes.status_codes import *
from codes.response_codes import *
from config.db_column_to_response import mapper
from helper.user import find_user_by_id, enroll_user_in_madrassa
from helper.madrassa_detail import find_madrassa_detail_by_id
from helper.role import find_role_by_id

user_api = Blueprint("user_api", __name__, url_prefix='')


@user_api.route(ADD_USER, methods=[POST])
@authorize_request
def add_user():
    request_body = request.get_json()
    missing = verify_param([gc.NAME, gc.FATHER_NAME, gc.CNIC, gc.EMAIL, gc.MOTHER_TONGUE, gc.CONTACT, gc.GENDER_ID,
                            gc.GUARDIAN_NAME, gc.GUARDIAN_CONTACT, gc.DATE_OF_BIRTH, gc.AGE], request_body)
    if missing:
        response = make_general_response(PARAMETER_MISSING, missing + " is missing")
        return response, BAD_REQUEST

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

    name = request_body.get(gc.NAME)
    fname = request_body.get(gc.FATHER_NAME)
    cnic = request_body.get(gc.CNIC)
    email = request_body.get(gc.EMAIL)
    mt = request_body.get(gc.MOTHER_TONGUE)
    contact = request_body.get(gc.CONTACT)
    gender_id = request_body.get(gc.GENDER_ID)
    guardian_name = request_body.get(gc.GUARDIAN_NAME)
    guardian_contact = request_body.get(gc.GUARDIAN_CONTACT)
    dob = request_body.get(gc.DATE_OF_BIRTH)
    age = request_body.get(gc.AGE)

    query = f"select * from {GENDER} where {ID}={gender_id}"
    r = select_query(query)
    result = r.fetchall()
    print(result)
    if len(result) == 0:
        response = make_general_response(GENDER_NOT_FOUND, f"GenderID {gender_id} doesn't exists")
        return response, BAD_REQUEST

    index = select_max(USER) + 1
    query = f"insert into {USER}({ID},{USER_NAME},{FATHER_NAME},{CNIC},{EMAIL},{MOTHER_TONGUE},{CONTACT}," \
            f"{GENDER_ID},{GUARDIAN_NAME},{GUARDIAN_CONTACT},{DOB},{AGE})" \
            f"values({index},'{name}','{fname}','{cnic}','{email}','{mt}','{contact}',{gender_id}," \
            f"'{guardian_name}','{guardian_contact}','{dob}','{age}')"
    print(query)
    r = insert_query(query)
    if r:
        query = f"select * from {USER} where {ID} = {index}"
        r = select_query(query)
        result = r.fetchall()
        for i in result:
            data = map_response(i, mapper)
        # data = {
        #     gc.ID: result[0][0],
        #     gc.NAME: result[0][1],
        #     gc.FATHER_NAME: result[0][2],
        #     gc.CNIC: result[0][3],
        #     gc.EMAIL: result[0][4],
        #     gc.MOTHER_TONGUE: result[0][5],
        #     gc.CONTACT: result[0][6],
        #     gc.GENDER_ID: result[0][7],
        #     gc.GUARDIAN_NAME: result[0][8],
        #     gc.GUARDIAN_CONTACT: result[0][9],
        #     gc.DATE_OF_BIRTH: result[0][10],
        #     gc.AGE: result[0][11],
        # }
        response = make_general_response(SUCCESS, "SUCCESS")
        response[gc.DATA] = data
        return response, CREATED

    else:
        response = make_general_response(FAIL, "FAIL")
        return response, BAD_REQUEST


@user_api.route(GET_USERS, methods=[GET])
@authorize_request
def get_users():
    query_params = request.args
    length_query_param = len(query_params)
    if length_query_param == 0:
        response = make_general_response(MISSING_QUERY_PARAM, "Query params are missing")
        return response, BAD_REQUEST

    elif not query_params.get(CNIC) and not query_params.get(CONTACT):
        response = make_general_response(INVALID_QUERY_PARAM, "Invalid query params")
        return response, BAD_REQUEST

    cnic = query_params.get(CNIC)
    contact = query_params.get(CONTACT)

    where_clause = ""

    if cnic or contact:
        where_clause = where_clause + "where"

    if cnic:
        if not validate_cnic(cnic):
            response = make_general_response(INVALID_PARAMETER, "Invalid CNIC")
            return response, BAD_REQUEST
        where_clause = where_clause + f" {CNIC}='{cnic}' "
        if contact:
            where_clause = where_clause + "and"

    if contact:
        if not validate_contact(contact):
            response = make_general_response(INVALID_PARAMETER, "Invalid Contact")
            return response, BAD_REQUEST
        where_clause = where_clause + f" ({CONTACT}='{contact}' or {GUARDIAN_CONTACT}='{contact}')"

    query = f"select * from {USER} " + where_clause
    print(query)
    r = select_query(query)
    result = r.fetchall()
    data = []
    for i in result:
        data.append(map_response(i, mapper))

    response = make_general_response(SUCCESS, "Success")
    response[gc.DATA] = data

    return response, OK


@user_api.route(ENROLL_USER, methods=[POST])
@authorize_request
def enroll_users():
    request_body = request.get_json()
    missing = verify_param([gc.USER_ID, gc.ENROLMENT_DATE, gc.MADRASSA_DETAIL, gc.ROLE_ID], request_body)
    if missing:
        response = make_general_response(PARAMETER_MISSING, missing + " is missing")
        return response, BAD_REQUEST

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

    enrolled, code = enroll_user_in_madrassa(user, madrassa_detail, role, enrollment_date)
    if enrolled:
        response = make_general_response(code,"SUCCESS")
        return response, OK
    response = make_general_response(code, "FAIL")
    return response, BAD_REQUEST

    return jsonify({request.base_url: request.method})
