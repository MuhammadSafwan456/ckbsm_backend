from flask import request, jsonify, Blueprint
from helper.authorization import authorize_request
from helper.request_response import *
from helper.user import find_enrollment_by_id
from helper.attendance import find_attendance_status_by_id, mark_attendance
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

attendance_api = Blueprint("attendance_api", __name__, url_prefix='')


@attendance_api.route(USER_ATTENDANCE, methods=[POST])
@authorize_request
@requires([gc.ENROLLMENT_ID, gc.DATE, gc.STATUS], body=gc.JSON)
def user_attendance():
    request_body = request.get_json()
    enrollment_id = request_body[gc.ENROLLMENT_ID]
    date = request_body[gc.DATE]
    status_id = request_body[gc.STATUS]

    enrollment = find_enrollment_by_id(enrollment_id)
    if not enrollment:
        response = make_general_response(ENROLLMENT_NOT_FOUND, "Enrollment not found")
        return response, BAD_REQUEST

    if not validate_date(date):
        response = make_general_response(INVALID_PARAMETER, "Invalid Date Format. Allowed Date format is YYYYMMDD")
        return response, BAD_REQUEST

    status = find_attendance_status_by_id(status_id)
    if not status:
        response = make_general_response(ATTENDANCE_STATUS_NOT_FOUND, "Attendance Status not found")
        return response, BAD_REQUEST

    marked, response_code, detail = mark_attendance(enrollment_id, date, status_id)
    response = make_general_response(response_code, detail)
    if marked:
        return response, OK
    return response, BAD_REQUEST



@attendance_api.route(BULK_USER_ATTENDANCE, methods=[POST])
@authorize_request
def bulk_user_attendance():
    return jsonify({request.base_url: request.method})


@attendance_api.route(GET_ALL_ATTENDANCE, methods=[GET])
@authorize_request
def get_all_attendance():
    return jsonify({request.base_url: request.method})
