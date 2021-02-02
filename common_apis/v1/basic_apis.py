# from database_layer.database import execute_query
# from config import database_config
# print(database_config.get_config("DB_USERNAME"))
# print("___________________first_______________")
# a = execute_query("SHOW TABLES")
# # print("A",a)
# for i in a:
#     print("i",i)
#
#
# print("\n___________________Second_______________")
# a = execute_query("SHOW TABLES")
# # print("A",a)
# for i in a:
#     print("j",i)

from constants.flask_constants import *
from constants.route_constants import *
from codes.status_codes import *
from codes.response_codes import *
from constants.general_constants import *
from flask import jsonify, request
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
    missing = verify_param([PASSWORD, USERNAME], request_body)
    if missing:
        response = make_missing_parameter_response(missing)
        return response, BAD_REQUEST

    response = {
        RESPONSE_CODE: SUCCESS,
        RESPONSE_DETAIL: "Admin Object"
    }
    return response, OK


@app.route(ADMIN_DASHBOARD, methods=[GET])
def admin_dashboard():
    return flask.jsonify({flask.request.base_url: flask.request.method})


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
