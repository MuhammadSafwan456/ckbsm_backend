from constants.flask_constants import *
from constants.route_constants import *
from codes.status_codes import *
from codes.response_codes import *
from constants.general_constants import *
from flask import jsonify, request
from database_layer.database import execute_query
import flask


app = flask.Flask(__name__)
app.config[DEBUG] = True


def make_missing_parameter_response(parameter):
    response = {
        RESPONSE_CODE: PARAMETER_MISSING,
        RESPONSE_DETAIL: parameter + " is missing"
    }
    return response


def verify_param(required, recieved):
    for req in required:
        if req in recieved:
            pass
        else:
            return req
    return None


@app.route(LOGIN, methods=[POST])
def login():
    request_body = request.get_json()
    missing = verify_param([USERNAME, PASSWORD], request_body)
    if missing:
        response = make_missing_parameter_response(missing)
        return response, BAD_REQUEST
    query = f"Select * from admin where username = '{request_body.get(USERNAME)}' and password = '{request_body.get(PASSWORD)}'"
    # print(query)
    r = execute_query(query)
    result = r.fetchall()
    if len(result) != 0:
        if result[0][0] == request_body.get(USERNAME) and result[0][1] == request_body.get(PASSWORD):
            response = {
                RESPONSE_CODE: SUCCESS,
                RESPONSE_DETAIL: "SUCCESS"
            }
            return response, OK
        else:
            response = {
                RESPONSE_CODE: ADMIN_NOT_FOUND,
                RESPONSE_DETAIL: "Incorrect Credentials"
            }
            return response, OK
    else:
        response = {
            RESPONSE_CODE: ADMIN_NOT_FOUND,
            RESPONSE_DETAIL: "Incorrect Credentials"
        }
        return response, OK


@app.route(ADMIN_DASHBOARD, methods=[GET])
def admin_dashboard():
    query_params = request.args
    length_query_param = len(query_params)
    # admin = request.args.get(ADMIN)
    if length_query_param == 0 :
        response = {
            RESPONSE_CODE: MISSING_QUERY_PARAM,
            RESPONSE_DETAIL: "Query params are missing"
        }
        return response, BAD_REQUEST

    elif len(query_params) > 1:
        response = {
            RESPONSE_CODE: ADDITIONAL_QUERY_PARAM,
            RESPONSE_DETAIL: "Additional Query params"
        }
        return response, BAD_REQUEST
    elif not query_params.get(ADMIN):
            response = {
                RESPONSE_CODE: INVALID_QUERY_PARAM,
                RESPONSE_DETAIL: "Invalid query params"
            }
            return response, BAD_REQUEST

    username = query_params.get(ADMIN)
    query = f"Select username from admin where username = '{username}' "
    print(query)
    r = execute_query(query)
    result = r.fetchall()
    if len(result) == 0:
        response = {
            RESPONSE_CODE: ADMIN_NOT_FOUND,
            RESPONSE_DETAIL: "Admin not found"
        }
        return response, OK

    query = "select count(id) from madrassa"
    r = execute_query(query)
    result = r.fetchall()
    madrassa_count = result[0][0]

    query = "select count(id) from course"
    r = execute_query(query)
    result = r.fetchall()
    course_count = result[0][0]

    query = "select count(id) from shift"
    r = execute_query(query)
    result = r.fetchall()
    shift_count = result[0][0]

    query = "select count(id) from enrollment where role_id = 0"
    r = execute_query(query)
    result = r.fetchall()
    teacher_count = result[0][0]

    query = "select count(id) from enrollment where role_id = 1"
    r = execute_query(query)
    result = r.fetchall()
    student_count = result[0][0]

    response = {
        RESPONSE_CODE: SUCCESS,
        RESPONSE_DETAIL: "Success",
        DATA: {
            'totalStudents': student_count,
            'totalTeachers':teacher_count,
            'totalShifts':shift_count,
            'totalCourses':course_count,
            'totalMadrassas':madrassa_count
        }
    }
    return response, OK


@app.route(GET_ROLES, methods=[GET])
def get_roles():
    return flask.jsonify({flask.request.base_url: flask.request.method})


@app.route(ADD_ROLES, methods=[POST])
def add_roles():
    return flask.jsonify({flask.request.base_url: flask.request.method})


@app.route(UPDATE_ROLES, methods=[PUT])
def update_roles():
    return flask.jsonify({flask.request.base_url: flask.request.method})


@app.route(DELETE_ROLES, methods=[DELETE])
def delete_roles():
    return flask.jsonify({flask.request.base_url: flask.request.method})



@app.route(GET_SHIFTS, methods=[GET])
def get_shifts():
    return flask.jsonify({flask.request.base_url: flask.request.method})



@app.route(ADD_SHIFT, methods=[POST])
def add_shifts():
    return flask.jsonify({flask.request.base_url: flask.request.method})



@app.route(UPDATE_SHIFT, methods=[PUT])
def update_shifts():
    return flask.jsonify({flask.request.base_url: flask.request.method})



@app.route(DELETE_SHIFTS, methods=[DELETE])
def delete_shifts():
    return flask.jsonify({flask.request.base_url: flask.request.method})



@app.route(GET_COURSES, methods=[GET])
def get_course():
    return flask.jsonify({flask.request.base_url: flask.request.method})



@app.route(ADD_COURSES, methods=[POST])
def add_courses():
    return flask.jsonify({flask.request.base_url: flask.request.method})



@app.route(UPDATE_COURSES, methods=[PUT])
def update_courses():
    return flask.jsonify({flask.request.base_url: flask.request.method})



@app.route(DELETE_COURSES, methods=[DELETE])
def delete_courses():
    return flask.jsonify({flask.request.base_url: flask.request.method})



@app.route(GET_MADRASSAS, methods=[GET])
def get_madrassas():
    return flask.jsonify({flask.request.base_url: flask.request.method})



@app.route(ADD_MADRASSAS, methods=[POST])
def add_madrassas():
    return flask.jsonify({flask.request.base_url: flask.request.method})



@app.route(UPDATE_MADRASSAS, methods=[PUT])
def update_madrassas():
    return flask.jsonify({flask.request.base_url: flask.request.method})



@app.route(DELETE_MADRASSAS, methods=[DELETE])
def delete_madrassas():
    return flask.jsonify({flask.request.base_url: flask.request.method})



@app.route(SET_MADRASSA_DETAILS, methods=[POST])
def set_madrassa_details():
    return flask.jsonify({flask.request.base_url: flask.request.method})



@app.route(GET_MADRASSA_DETAILS, methods=[GET])
def get_madrassa_details():
    return flask.jsonify({flask.request.base_url: flask.request.method})



@app.route(ADD_USER, methods=[POST])
def add_user():
    return flask.jsonify({flask.request.base_url: flask.request.method})



@app.route(GET_USERS, methods=[GET])
def get_users():
    return flask.jsonify({flask.request.base_url: flask.request.method})



@app.route(ENROLL_USER, methods=[POST])
def enroll_users():
    return flask.jsonify({flask.request.base_url: flask.request.method})


@app.route(USER_ATTENDANCE, methods=[POST])
def user_attendance():
    return flask.jsonify({flask.request.base_url: flask.request.method})



@app.route(BULK_USER_ATTENDANCE, methods=[POST])
def bulk_user_attendance():
    return flask.jsonify({flask.request.base_url: flask.request.method})



@app.route(GET_ALL_ATTENDANCE, methods=[GET])
def get_all_attendance():
    return flask.jsonify({flask.request.base_url: flask.request.method})


if __name__ == '__main__':
    app.run()
