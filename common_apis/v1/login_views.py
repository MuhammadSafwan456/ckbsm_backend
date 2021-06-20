"""
Author : s.aryani456@gmail.com
Views related to login mechanism
"""


from jwt import encode
from hashlib import sha256
from flask import request

from constants import general_constants as gc
from constants.route_constants import LOGIN, ADMIN_DASHBOARD
from flask import Blueprint, current_app
from helper.request_response import make_general_response
from helper import database
from constants.flask_constants import GET, SECRET_KEY
from codes.status_codes import OK, UNAUTHORIZED
from constants.table_names import ADMIN
from helper.authorization import authorize_request
from constants.column_names import USERNAME, PASSWORD, ROLE_ID, ID
from codes.status_codes import BAD_REQUEST
from codes.response_codes import SUCCESS, ADMIN_NOT_FOUND, FAIL
from codes.response_codes import MISSING_QUERY_PARAM, ADDITIONAL_QUERY_PARAM, INVALID_QUERY_PARAM
from constants.table_names import MADRASSA, COURSE, SHIFT, ENROLLMENT

login_api = Blueprint("login_api", __name__, url_prefix='')


@login_api.route(LOGIN, methods=[GET])
def login():
    auth_body = request.authorization
    if not auth_body or not auth_body.get(gc.USERNAME) or not auth_body.get(gc.PASSWORD):
        response = make_general_response(FAIL, "Authorization Missing")
        return response, UNAUTHORIZED

    query = f"Select * from {ADMIN} where {USERNAME} = '{auth_body.get(gc.USERNAME)}' and" \
            f" {PASSWORD} = '{auth_body.get(gc.PASSWORD)}' "

    r = database.select_query(query)
    result = r.fetchall()
    if len(result) != 0:
        if result[0][USERNAME] == auth_body.get(USERNAME) and result[0][PASSWORD] == auth_body.get(PASSWORD):
            response = make_general_response(SUCCESS, "SUCCESS")
            token = encode(
                {
                    USERNAME: auth_body.get(gc.USERNAME),
                    PASSWORD: sha256(auth_body.get(gc.PASSWORD).encode(gc.ASCII)).hexdigest()

                }, current_app.config[SECRET_KEY])
            response[gc.TOKEN] = token

            return response, OK
        else:
            response = make_general_response(ADMIN_NOT_FOUND, "Could not verify")
            return response, UNAUTHORIZED
    else:
        response = make_general_response(ADMIN_NOT_FOUND, "Could not verify")
        return response, UNAUTHORIZED


@login_api.route(ADMIN_DASHBOARD, methods=[GET])
@authorize_request
def admin_dashboard():
    def first_row_first_col(query):
        res = database.select_query(query)
        res = res.fetchall()
        count = res[0][ID]
        return count

    query_params = request.args
    length_query_param = len(query_params)
    if length_query_param == 0:
        response = make_general_response(MISSING_QUERY_PARAM, "Query params are missing")
        return response, BAD_REQUEST

    elif len(query_params) > 1:
        response = make_general_response(ADDITIONAL_QUERY_PARAM, "Additional Query params")
        return response, BAD_REQUEST

    elif not query_params.get(gc.ADMIN):
        response = make_general_response(INVALID_QUERY_PARAM, "Invalid query params")
        return response, BAD_REQUEST

    username = query_params.get(gc.ADMIN)

    query = f"Select {USERNAME} from {ADMIN} where {USERNAME} = '{username}' "
    r = database.select_query(query)
    result = r.fetchall()

    if len(result) == 0:
        response = make_general_response(ADMIN_NOT_FOUND, "Admin not found")
        return response, OK

    query = f"select count({ID}) as {ID} from {MADRASSA}"
    madrassa_count = first_row_first_col(query)

    query = f"select count({ID}) as {ID} from {COURSE}"
    course_count = first_row_first_col(query)

    query = f"select count({ID}) as {ID} from {SHIFT}"
    shift_count = first_row_first_col(query)

    query = f"select count({ID}) as {ID} from {ENROLLMENT} where {ROLE_ID} = 0"
    teacher_count = first_row_first_col(query)

    query = f"select count({ID}) as {ID} from {ENROLLMENT} where {ROLE_ID} = 1"
    student_count = first_row_first_col(query)

    response = make_general_response(SUCCESS, "Success")
    response[gc.DATA] = {
        'totalStudents': student_count,
        'totalTeachers': teacher_count,
        'totalShifts': shift_count,
        'totalCourses': course_count,
        'totalMadrassas': madrassa_count
    }
    return response, OK
