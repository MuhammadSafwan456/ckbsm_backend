from constants.flask_constants import *
from constants.table_names import *
from constants.route_constants import *
from codes.status_codes import *
from codes.response_codes import *
import constants.general_constants as gc
from config.app_config import JWT_SECRET_KEY
from constants.column_names import *
from flask import request
from database_layer.database import select_query, insert_query
from hashlib import sha256
from functools import wraps
import flask
import jwt
import datetime

app = flask.Flask(__name__)
app.config[DEBUG] = True
app.config[SECRET_KEY] = sha256(JWT_SECRET_KEY.encode(gc.ASCII)).hexdigest()


def authorize_request(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        token = None
        if X_ACCESS_TOKEN in request.headers:
            token = request.headers[X_ACCESS_TOKEN]

        if not token:
            response = make_general_response(MISSING_TOKEN, 'token is missing')
            return response, UNAUTHORIZED

        try:
            algorithm = gc.SHA256
            data = jwt.decode(token, app.config[SECRET_KEY], algorithms=[algorithm])
            query = f"Select {PASSWORD} from {ADMIN} where {USERNAME} = '{data.get(gc.USERNAME)}'"
            r = select_query(query)
            result = r.fetchall()
            password = result[0][0]
            hashed_password = sha256(password.encode(gc.ASCII)).hexdigest()
            if hashed_password == data.get(gc.PASSWORD):
                return f(*args, **kwargs)

        except:
            response = make_general_response(INVALID_TOKEN, 'token is invalid')
            return response, UNAUTHORIZED

    return wrap


def select_max(table):
    query = f'select max({ID}) from {table}'
    r = select_query(query)
    result = r.fetchall()
    if result[0][0]:
        return result[0][0]
    return 0


def make_general_response(code, detail):
    response = {
        gc.RESPONSE_CODE: code,
        gc.RESPONSE_DETAIL: detail
    }
    return response


def make_missing_parameter_response(parameter):
    response = {
        gc.RESPONSE_CODE: PARAMETER_MISSING,
        gc.RESPONSE_DETAIL: parameter + " is missing"
    }
    return response


def verify_param(required, received):
    for req in required:
        if req in received:
            pass
        else:
            return req
    return None


@app.route(LOGIN, methods=[GET])
def login():
    auth_body = request.authorization
    if not auth_body or not auth_body.get(gc.USERNAME) or not auth_body.get(gc.PASSWORD):
        response = make_general_response(FAIL, "Authorization Missing")
        return response, UNAUTHORIZED

    # missing = verify_param([USERNAME, PASSWORD], auth_body)
    # if missing:
    #     response = make_general_response(PARAMETER_MISSING, missing + " is missing")
    #     return response, BAD_REQUEST

    query = f"Select * from {ADMIN} where {USERNAME} = '{auth_body.get(gc.USERNAME)}' and" \
            f" {PASSWORD} = '{auth_body.get(gc.PASSWORD)}' "

    r = select_query(query)
    result = r.fetchall()
    if len(result) != 0:
        if result[0][0] == auth_body.get(USERNAME) and result[0][1] == auth_body.get(PASSWORD):
            response = make_general_response(SUCCESS, "SUCCESS")
            token = jwt.encode(
                {
                    USERNAME: auth_body.get(gc.USERNAME),
                    PASSWORD: sha256(auth_body.get(gc.PASSWORD).encode(gc.ASCII)).hexdigest()

                }, app.config[SECRET_KEY])
            response[gc.TOKEN] = token

            return response, OK
        else:
            response = make_general_response(ADMIN_NOT_FOUND, "Could not verify")
            return response, UNAUTHORIZED
    else:
        response = make_general_response(ADMIN_NOT_FOUND, "Could not verify")
        return response, UNAUTHORIZED


@app.route(ADMIN_DASHBOARD, methods=[GET])
@authorize_request
def admin_dashboard():
    def first_row_first_col(query):
        res = select_query(query)
        res = res.fetchall()
        count = res[0][0]
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
    r = select_query(query)
    result = r.fetchall()
    if len(result) == 0:
        response = make_general_response(ADMIN_NOT_FOUND, "Admin not found")
        return response, OK

    query = f"select count({ID}) from {MADRASSA}"
    madrassa_count = first_row_first_col(query)

    query = f"select count({ID}) from {COURSE}"
    course_count = first_row_first_col(query)

    query = f"select count({ID}) from {SHIFT}"
    shift_count = first_row_first_col(query)

    query = f"select count({ID}) from {ENROLLMENT} where {ROLE_ID} = 0"
    teacher_count = first_row_first_col(query)

    query = f"select count({ID}) from {ENROLLMENT} where {ROLE_ID} = 1"
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


@app.route(GET_ROLES, methods=[GET])
@authorize_request
def get_roles():
    query = f"select * from {ROLE}"
    r = select_query(query)
    result = r.fetchall()
    data = []
    for i in result:
        data.append({
            gc.ID: i[0],
            gc.NAME: i[1]
        })

    response = make_general_response(SUCCESS, "Success")
    response[gc.DATA] = data
    return response, OK


@app.route(ADD_ROLES, methods=[POST])
@authorize_request
def add_roles():
    request_body = request.get_json()
    missing = verify_param([gc.NAME], request_body)
    if missing:
        response = make_general_response(PARAMETER_MISSING, missing + " is missing")
        return response, BAD_REQUEST
    index = select_max(ROLE) + 1

    query = f"insert into {ROLE}({ID}, {ROLE_NAME}) values({index},'{request_body[gc.NAME]}')"
    r = insert_query(query)
    if r:
        query = f"select * from {ROLE} where id = {index}"
        r = select_query(query)
        result = r.fetchall()
        data = {
            gc.ID: result[0][0],
            gc.NAME: result[0][1]
        }
        response = make_general_response(SUCCESS, "SUCCESS")
        response[gc.DATA] = data
        return response, CREATED

    else:
        response = make_general_response(FAIL, "FAIL")
        return response, OK


@app.route(UPDATE_ROLES, methods=[PUT])
@authorize_request
def update_roles():
    request_body = request.get_json()
    missing = verify_param([gc.ID, gc.NAME], request_body)
    if missing:
        response = make_general_response(PARAMETER_MISSING, missing + " is missing")
        return response, BAD_REQUEST

    query = f"update {ROLE} set {ROLE_NAME} = '{request_body[gc.NAME]}' where id = {request_body[gc.ID]}"
    r = insert_query(query)
    if r:
        query = f"select * from {ROLE} where {ID} = {request_body[gc.ID]}"
        r = select_query(query)
        result = r.fetchall()
        data = {
            gc.ID: result[0][0],
            gc.NAME: result[0][1]
        }
        response = make_general_response(SUCCESS, "SUCCESS")
        response[gc.DATA] = data
        return response, CREATED

    else:
        response = make_general_response(ROLE_NOT_FOUND, "RoleID not found")
        return response, OK


@app.route(DELETE_ROLES, methods=[DELETE])
@authorize_request
def delete_roles():
    query_params = request.args
    length_query_param = len(query_params)
    if length_query_param == 0:
        response = make_general_response(MISSING_QUERY_PARAM, "Query params are missing")
        return response, BAD_REQUEST

    elif len(query_params) > 1:
        response = make_general_response(ADDITIONAL_QUERY_PARAM, "Additional Query params")
        return response, BAD_REQUEST

    elif not query_params.get(gc.ID):
        response = make_general_response(INVALID_QUERY_PARAM, "Invalid query params")
        return response, BAD_REQUEST

    query = f'delete from {ROLE} where {ID} ={query_params[gc.ID]}'
    r = insert_query(query)
    if r:
        response = make_general_response(SUCCESS, "SUCCESS")
        response[gc.DELETED] = r
        return response, CREATED

    else:
        response = make_general_response(ROLE_NOT_FOUND, "RoleID not found")
        response[gc.DELETED] = r
        return response, OK


@app.route(GET_SHIFTS, methods=[GET])
@authorize_request
def get_shifts():
    query = f"select * from {SHIFT}"
    r = select_query(query)
    result = r.fetchall()
    data = []
    for i in result:
        data.append({
            ID: i[0],
            gc.NAME: i[1],
            gc.START_TIME: str(i[2]),
            gc.END_TIME: str(i[3])
        })

    response = make_general_response(SUCCESS, "Success")
    response[gc.DATA] = data
    return response, OK


@app.route(ADD_SHIFT, methods=[POST])
@authorize_request
def add_shifts():
    request_body = request.get_json()
    missing = verify_param([gc.NAME, gc.START_TIME, gc.END_TIME], request_body)
    if missing:
        response = make_general_response(PARAMETER_MISSING, missing + " is missing")
        return response, BAD_REQUEST
    index = select_max(SHIFT) + 1

    query = f"insert into shift(id,shift_name,start_time,end_time) " \
            f"values({index},'{request_body[gc.NAME]}','{request_body[gc.START_TIME]}','{request_body[gc.END_TIME]}')"
    r = insert_query(query)
    if r:
        query = f"select * from {SHIFT} where {ID} = {index}"
        r = select_query(query)
        result = r.fetchall()
        data = {
            gc.ID: result[0][0],
            gc.NAME: result[0][1],
            gc.START_TIME: str(result[0][2]),
            gc.END_TIME: str(result[0][3]),
        }
        response = make_general_response(SUCCESS, "SUCCESS")
        response[gc.DATA] = data
        return response, CREATED

    else:
        response = make_general_response(FAIL, "FAIL")
        return response, OK

    # return flask.jsonify({flask.request.base_url: flask.request.method})


@app.route(UPDATE_SHIFT, methods=[PUT])
@authorize_request
def update_shifts():
    request_body = request.get_json()
    missing = verify_param([gc.ID, gc.NAME, gc.START_TIME, gc.END_TIME], request_body)
    if missing:
        response = make_general_response(PARAMETER_MISSING, missing + " is missing")
        return response, BAD_REQUEST

    query = f"update {SHIFT}" \
            f" set {SHIFT_NAME} = '{request_body[gc.NAME]}' , {START_TIME} = '{request_body[gc.START_TIME]}', " \
            f"{END_TIME}= '{request_body[gc.END_TIME]}' where {ID} = {request_body[gc.ID]}"
    r = insert_query(query)
    if r:
        query = f"select * from {SHIFT} where {ID} = {request_body[gc.ID]}"
        r = select_query(query)
        result = r.fetchall()
        data = {
            gc.ID: result[0][0],
            gc.NAME: result[0][1],
            gc.START_TIME: str(result[0][2]),
            gc.END_TIME: str(result[0][3]),
        }
        response = make_general_response(SUCCESS, "SUCCESS")
        response[gc.DATA] = data
        return response, CREATED

    else:
        response = make_general_response(SHIFT_NOT_FOUND, "ShiftID not found")
        return response, OK
    # return flask.jsonify({flask.request.base_url: flask.request.method})


@app.route(DELETE_SHIFTS, methods=[DELETE])
@authorize_request
def delete_shifts():
    query_params = request.args
    length_query_param = len(query_params)
    if length_query_param == 0:
        response = make_general_response(MISSING_QUERY_PARAM, "Query params are missing")
        return response, BAD_REQUEST

    elif len(query_params) > 1:
        response = make_general_response(ADDITIONAL_QUERY_PARAM, "Additional Query params")
        return response, BAD_REQUEST

    elif not query_params.get(ID):
        response = make_general_response(INVALID_QUERY_PARAM, "Invalid query params")
        return response, BAD_REQUEST

    query = f'delete from {SHIFT} where {ID}={query_params[gc.ID]}'
    r = insert_query(query)
    if r:
        response = make_general_response(SUCCESS, "SUCCESS")
        response[gc.DELETED] = r
        return response, CREATED

    else:
        response = make_general_response(SHIFT_NOT_FOUND, "ShiftID not found")
        response[gc.DELETED] = r
        return response, OK

    # return flask.jsonify({flask.request.base_url: flask.request.method})


@app.route(GET_COURSES, methods=[GET])
@authorize_request
def get_course():
    query = f"select * from {COURSE}"
    r = select_query(query)
    result = r.fetchall()
    data = []
    for i in result:
        data.append({
            gc.ID: i[0],
            gc.NAME: i[1]
        })

    response = make_general_response(SUCCESS, "Success")
    response[gc.DATA] = data
    return response, OK


@app.route(ADD_COURSES, methods=[POST])
@authorize_request
def add_courses():
    request_body = request.get_json()
    missing = verify_param([gc.NAME], request_body)
    if missing:
        response = make_general_response(PARAMETER_MISSING, missing + " is missing")
        return response, BAD_REQUEST
    index = select_max(COURSE) + 1

    query = f"insert into {COURSE}({ID},{COURSE_NAME}) values({index},'{request_body[gc.NAME]}')"
    r = insert_query(query)
    if r:
        query = f"select * from {COURSE} where {ID} = {index}"
        r = select_query(query)
        result = r.fetchall()
        data = {
            gc.ID: result[0][0],
            gc.NAME: result[0][1]
        }
        response = make_general_response(SUCCESS, "SUCCESS")
        response[gc.DATA] = data
        return response, CREATED

    else:
        response = make_general_response(FAIL, "FAIL")
        return response, OK


@app.route(UPDATE_COURSES, methods=[PUT])
@authorize_request
def update_courses():
    request_body = request.get_json()
    missing = verify_param([gc.ID, gc.NAME], request_body)
    if missing:
        response = make_general_response(PARAMETER_MISSING, missing + " is missing")
        return response, BAD_REQUEST

    query = f"update {COURSE} set {COURSE_NAME} = '{request_body[gc.NAME]}' where {ID} = {request_body[gc.ID]}"
    r = insert_query(query)
    if r:
        query = f"select * from {COURSE} where {ID} = {request_body[ID]}"

        r = select_query(query)
        result = r.fetchall()
        data = {
            gc.ID: result[0][0],
            gc.NAME: result[0][1]
        }
        response = make_general_response(SUCCESS, "SUCCESS")
        response[gc.DATA] = data
        return response, CREATED

    else:
        response = make_general_response(COURSE_NOT_FOUND, "CourseID not found")
        return response, OK


@app.route(DELETE_COURSES, methods=[DELETE])
@authorize_request
def delete_courses():
    query_params = request.args
    length_query_param = len(query_params)
    if length_query_param == 0:
        response = make_general_response(MISSING_QUERY_PARAM, "Query params are missing")
        return response, BAD_REQUEST

    elif len(query_params) > 1:
        response = make_general_response(ADDITIONAL_QUERY_PARAM, "Additional Query params")
        return response, BAD_REQUEST

    elif not query_params.get(ID):
        response = make_general_response(INVALID_QUERY_PARAM, "Invalid query params")
        return response, BAD_REQUEST

    query = f'delete from {COURSE} where {ID} = {query_params[gc.ID]}'
    r = insert_query(query)
    if r:
        response = make_general_response(SUCCESS, "SUCCESS")
        response[gc.DELETED] = r
        return response, CREATED

    else:
        response = make_general_response(COURSE_NOT_FOUND, "CourseID not found")
        response[gc.DELETED] = r
        return response, OK


@app.route(GET_MADRASSAS, methods=[GET])
@authorize_request
def get_madrassas():
    query = f"select * from {MADRASSA}"
    r = select_query(query)
    result = r.fetchall()
    data = []
    for i in result:
        data.append({
            gc.ID: i[0],
            gc.NAME: i[1]
        })

    response = make_general_response(SUCCESS, "Success")
    response[gc.DATA] = data
    return response, OK


@app.route(ADD_MADRASSAS, methods=[POST])
@authorize_request
def add_madrassas():
    request_body = request.get_json()
    missing = verify_param([gc.NAME], request_body)
    if missing:
        response = make_general_response(PARAMETER_MISSING, missing + " is missing")
        return response, BAD_REQUEST
    index = select_max(MADRASSA) + 1

    query = f"insert into {MADRASSA}({ID},{MADRASSA_NAME}) values({index},'{request_body[gc.NAME]}')"
    r = insert_query(query)
    if r:
        query = f"select * from {MADRASSA} where {ID} = {index}"
        r = select_query(query)
        result = r.fetchall()
        data = {
            gc.ID: result[0][0],
            gc.NAME: result[0][1]
        }
        response = make_general_response(SUCCESS, "SUCCESS")
        response[gc.DATA] = data
        return response, CREATED

    else:
        response = make_general_response(FAIL, "FAIL")
        return response, OK


@app.route(UPDATE_MADRASSAS, methods=[PUT])
@authorize_request
def update_madrassas():
    request_body = request.get_json()
    missing = verify_param([gc.ID, gc.NAME], request_body)
    if missing:
        response = make_general_response(PARAMETER_MISSING, missing + " is missing")
        return response, BAD_REQUEST

    query = f"update {MADRASSA} set {MADRASSA_NAME} = '{request_body[gc.NAME]}' where id = {request_body[gc.ID]}"
    r = insert_query(query)
    if r:
        query = f"select * from {MADRASSA} where {ID} = {request_body[gc.ID]}"
        r = select_query(query)
        result = r.fetchall()
        data = {
            gc.ID: result[0][0],
            gc.NAME: result[0][1]
        }
        response = make_general_response(SUCCESS, "SUCCESS")
        response[gc.DATA] = data
        return response, CREATED

    else:
        response = make_general_response(MADRASSA_NOT_FOUND, "MadrassaID not found")
        return response, OK


@app.route(DELETE_MADRASSAS, methods=[DELETE])
@authorize_request
def delete_madrassas():
    query_params = request.args
    length_query_param = len(query_params)
    if length_query_param == 0:
        response = make_general_response(MISSING_QUERY_PARAM, "Query params are missing")
        return response, BAD_REQUEST

    elif len(query_params) > 1:
        response = make_general_response(ADDITIONAL_QUERY_PARAM, "Additional Query params")
        return response, BAD_REQUEST

    elif not query_params.get(ID):
        response = make_general_response(INVALID_QUERY_PARAM, "Invalid query params")
        return response, BAD_REQUEST

    query = f'delete from {MADRASSA} where {ID}={query_params[gc.ID]}'
    r = insert_query(query)
    if r:
        response = make_general_response(SUCCESS, "SUCCESS")
        response[gc.DELETED] = r
        return response, CREATED

    else:
        response = make_general_response(MADRASSA_NOT_FOUND, "MadrassaID not found")
        response[gc.DELETED] = r
        return response, OK


@app.route(SET_MADRASSA_DETAILS, methods=[POST])
@authorize_request
def set_madrassa_details():
    return flask.jsonify({flask.request.base_url: flask.request.method})


@app.route(GET_MADRASSA_DETAILS, methods=[GET])
@authorize_request
def get_madrassa_details():
    return flask.jsonify({flask.request.base_url: flask.request.method})


@app.route(ADD_USER, methods=[POST])
@authorize_request
def add_user():
    return flask.jsonify({flask.request.base_url: flask.request.method})


@app.route(GET_USERS, methods=[GET])
@authorize_request
def get_users():
    return flask.jsonify({flask.request.base_url: flask.request.method})


@app.route(ENROLL_USER, methods=[POST])
@authorize_request
def enroll_users():
    return flask.jsonify({flask.request.base_url: flask.request.method})


@app.route(USER_ATTENDANCE, methods=[POST])
@authorize_request
def user_attendance():
    return flask.jsonify({flask.request.base_url: flask.request.method})


@app.route(BULK_USER_ATTENDANCE, methods=[POST])
@authorize_request
def bulk_user_attendance():
    return flask.jsonify({flask.request.base_url: flask.request.method})


@app.route(GET_ALL_ATTENDANCE, methods=[GET])
@authorize_request
def get_all_attendance():
    return flask.jsonify({flask.request.base_url: flask.request.method})


if __name__ == '__main__':
    app.run()
