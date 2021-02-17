from constants.flask_constants import *
from constants.table_names import *
from constants.route_constants import *
from codes.status_codes import *
from codes.response_codes import *
import constants.general_constants as gc
from config.app_config import JWT_SECRET_KEY
from config.db_column_to_response import mapper
from constants.column_names import *
from flask import request
from database_layer.database import select_query, insert_query
from hashlib import sha256
from functools import wraps
import flask
import jwt
import re
import json
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

        # try:
        algorithm = gc.SHA256
        data = jwt.decode(token, app.config[SECRET_KEY], algorithms=[algorithm])
        query = f"Select {PASSWORD} from {ADMIN} where {USERNAME} = '{data.get(gc.USERNAME)}'"
        r = select_query(query)
        result = r.fetchall()
        password = result[0][PASSWORD]
        hashed_password = sha256(password.encode(gc.ASCII)).hexdigest()
        if hashed_password == data.get(gc.PASSWORD):
            return f(*args, **kwargs)

        # except:
        #     response = make_general_response(INVALID_TOKEN, 'token is invalid')
        #     return response, UNAUTHORIZED

    return wrap


def select_max(table):
    query = f'select max({ID}) as {ID} from {table}'
    r = select_query(query)
    result = r.fetchall()
    print("_______________________________",result)
    if result[0].get(ID):
        return result[0].get(ID)
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


def validate_cnic(cnic):
    result = re.match("^[0-9]{5}-[0-9]{7}-[0-9]$", cnic)
    if result is None:
        return False
    return True


def validate_time(time):
    try:
        if not len(time) == 4:
            return False, None
        hour = time[0:2]
        mint = time[2:4]
        if int(hour) > 23 or int(mint) > 60:
            return False, None
    except:
        return False, None
    return True, time+"00"


def validate_email(email):
    result = re.match("^.+[ @].+[.].+", email)
    if result is None:
        return False
    return True


def validate_contact(number):
    result = re.match("^03[0-4][0-9]-[0-9]{7}", number)
    if result is None:
        return False
    return True


def validate_date(date):
    if not len(date) == 8:
        return False
    yy = date[0:4]
    mm = date[4:6]
    dd = date[6:8]
    try:
        datetime.datetime(int(yy), int(mm), int(dd))
    except ValueError:
        return False
    return True


def map_response(original_dict, mapper):
    data = {}
    for key in original_dict:
        data[mapper[key]] = original_dict[key]
    return data


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
        if result[0][USERNAME] == auth_body.get(USERNAME) and result[0][PASSWORD] == auth_body.get(PASSWORD):
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
    r = select_query(query)
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


@app.route(GET_ROLES, methods=[GET])
@authorize_request
def get_roles():
    query = f"select * from {ROLE}"
    r = select_query(query)
    result = r.fetchall()
    data = []
    for i in result:
        mapped_data = map_response(i, mapper)
        data.append(mapped_data)
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
        # data = {
        #     gc.ID: result[0][0],
        #     gc.NAME: result[0][1]
        # }
        data = map_response(result[0], mapper)
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
        data = map_response(result[0],mapper)
        # data = {
        #     gc.ID: result[0][0],
        #     gc.NAME: result[0][1]
        # }
        response = make_general_response(SUCCESS, "SUCCESS")
        response[gc.DATA] = data
        return response, CREATED

    else:
        response = make_general_response(ROLE_NOT_FOUND, "RoleID not found or Already Updated")
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

    flag, start_time = validate_time(request_body[gc.START_TIME])
    if not flag:
        response = make_general_response(INVALID_PARAMETER, "Invalid Start Time format allowed is hhmm")
        return response, BAD_REQUEST

    flag, end_time = validate_time(request_body[gc.END_TIME])
    if not flag:
        response = make_general_response(INVALID_PARAMETER, "Invalid End Time format allowed is hhmm")
        return response, BAD_REQUEST

    index = select_max(SHIFT) + 1

    query = f"insert into shift(id,shift_name,start_time,end_time) " \
            f"values({index},'{request_body[gc.NAME]}','{start_time}','{end_time}')"
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

    flag, start_time = validate_time(request_body[gc.START_TIME])
    if not flag:
        response = make_general_response(INVALID_PARAMETER, "Invalid Start Time format allowed is hhmm")
        return response, BAD_REQUEST

    flag, end_time = validate_time(request_body[gc.END_TIME])
    if not flag:
        response = make_general_response(INVALID_PARAMETER, "Invalid End Time format allowed is hhmm")
        return response, BAD_REQUEST


    query = f"update {SHIFT}" \
            f" set {SHIFT_NAME} = '{request_body[gc.NAME]}' , {START_TIME} = '{start_time}', " \
            f"{END_TIME}= '{end_time}' where {ID} = {request_body[gc.ID]}"
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
        return response, BAD_REQUEST


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


@app.route(GET_GENDER, methods=[GET])
@authorize_request
def get_gender():
    query = f"select * from {GENDER}"
    r = select_query(query)
    result = r.fetchall()
    data = []
    for i in result:
        data.append({
            gc.ID: i[0],
            gc.GENDER: i[1]
        })
    response = make_general_response(SUCCESS, "Success")
    response[gc.DATA] = data
    return response, OK


@app.route(ADD_GENDER, methods=[POST])
@authorize_request
def add_gender():
    request_body = request.get_json()
    missing = verify_param([gc.GENDER], request_body)
    if missing:
        response = make_general_response(PARAMETER_MISSING, missing + " is missing")
        return response, BAD_REQUEST
    index = select_max(GENDER) + 1

    query = f"insert into {GENDER}({ID},{GENDER}) values({index},'{request_body[gc.GENDER]}')"
    r = insert_query(query)
    if r:
        query = f"select * from {GENDER} where {ID} = {index}"
        r = select_query(query)
        result = r.fetchall()
        data = {
            gc.ID: result[0][0],
            gc.GENDER: result[0][1]
        }
        response = make_general_response(SUCCESS, "SUCCESS")
        response[gc.DATA] = data
        return response, CREATED

    else:
        response = make_general_response(FAIL, "FAIL")
        return response, OK


@app.route(UPDATE_GENDER, methods=[PUT])
@authorize_request
def update_gender():
    request_body = request.get_json()
    missing = verify_param([gc.ID, gc.GENDER], request_body)
    if missing:
        response = make_general_response(PARAMETER_MISSING, missing + " is missing")
        return response, BAD_REQUEST

    query = f"update {GENDER} set {GENDER} = '{request_body[gc.GENDER]}' where id = {request_body[gc.ID]}"
    r = insert_query(query)
    if r:
        query = f"select * from {GENDER} where {ID} = {request_body[gc.ID]}"
        r = select_query(query)
        result = r.fetchall()
        data = {
            gc.ID: result[0][0],
            gc.GENDER: result[0][1]
        }
        response = make_general_response(SUCCESS, "SUCCESS")
        response[gc.DATA] = data
        return response, CREATED

    else:
        response = make_general_response(GENDER_NOT_FOUND, "GenderID not found")
        return response, OK


@app.route(DELETE_GENDER, methods=[DELETE])
@authorize_request
def delete_gender():
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

    query = f'delete from {GENDER} where {ID}={query_params[gc.ID]}'
    r = insert_query(query)
    if r:
        response = make_general_response(SUCCESS, "SUCCESS")
        response[gc.DELETED] = r
        return response, CREATED

    else:
        response = make_general_response(GENDER_NOT_FOUND, "GenderID not found")
        response[gc.DELETED] = r
        return response, OK


@app.route(SET_MADRASSA_DETAILS, methods=[POST])
@authorize_request
def set_madrassa_details():
    request_body = request.get_json()
    missing = verify_param([gc.MADRASSA_ID, gc.SHIFT_ID, gc.COURSE_ID], request_body)
    if missing:
        response = make_general_response(PARAMETER_MISSING, missing + " is missing")
        return response, BAD_REQUEST

    index = select_max(MADRASSA_DETAILS) + 1

    shift_id = request_body[gc.SHIFT_ID]
    course_id = request_body[gc.COURSE_ID]
    madrassa_id = request_body[gc.MADRASSA_ID]
    query = f"insert into {MADRASSA_DETAILS}({ID}, {SHIFT_ID}, {COURSE_ID}, {MADRASSA_ID})" \
            f"values({index}, {shift_id}, {course_id}, {madrassa_id})"

    r = insert_query(query)
    if r:
        query = f"select distinct {SHIFT_ID},{SHIFT_NAME},{START_TIME},{END_TIME} " \
                f"from {MADRASSA_DETAILS} inner join {SHIFT} on " \
                f"{MADRASSA_DETAILS}.{SHIFT_ID} = {SHIFT}.{ID} " \
                f"where {SHIFT_ID} = {shift_id}"
        r = select_query(query)
        result = r.fetchall()
        shift_object = {
            gc.ID: result[0][0],
            gc.NAME: result[0][1],
            gc.START_TIME: str(result[0][2]),
            gc.END_TIME: str(result[0][3])
        }

        query = f"select distinct {MADRASSA_ID},{MADRASSA_NAME} from " \
                f"{MADRASSA_DETAILS} inner join {MADRASSA} " \
                f"on {MADRASSA_DETAILS}.{MADRASSA_ID} = {MADRASSA}.{ID} " \
                f"where {MADRASSA_ID} = {madrassa_id}"
        r = select_query(query)
        result = r.fetchall()
        madrassa_object = {
            gc.ID: result[0][0],
            gc.NAME: result[0][1]
        }

        query = f"select distinct {COURSE_ID},{COURSE_NAME} from " \
                    f"{MADRASSA_DETAILS} inner join {COURSE} " \
                f"on {MADRASSA_DETAILS}.{COURSE_ID} = {COURSE}.{ID} " \
                f"where {COURSE_ID} = {course_id}"
        r = select_query(query)
        result = r.fetchall()
        course_object = {
            gc.ID: result[0][0],
            gc.NAME: result[0][1]
        }
        response = make_general_response(SUCCESS, "SUCCESS")
        response[gc.DATA] = {}
        response[gc.DATA][MADRASSA] = madrassa_object
        response[gc.DATA][SHIFT] = shift_object
        response[gc.DATA][COURSE] = course_object
        return response, CREATED

    else:
        response = make_general_response(FAIL, "FAIL")
        return response, OK
# def first_row_first_col(query):
    #     res = select_query(query)
    #     res = res.fetchall()
    #     count = res[0][0]
    #     return count
    #
    # request_body = request.get_json()
    # missing = verify_param([gc.MADRASSA_ID, gc.SHIFT_ID, gc.COURSE_ID], request_body)
    # if missing:
    #     response = make_general_response(PARAMETER_MISSING, missing + " is missing")
    #     return response, BAD_REQUEST
    #
    # madrassa_id = request_body.get(gc.MADRASSA_ID)
    # shift_id = request_body.get(gc.SHIFT_ID)
    # course_id = request_body.get(gc.COURSE_ID)
    #
    # query = f"select count({ID}) from {MADRASSA} where {ID} = {madrassa_id}"
    # m_count = first_row_first_col(query)
    #
    # query = f"select count({ID}) from {SHIFT}  where {ID} = {shift_id}"
    # s_count = first_row_first_col(query)
    #
    # query = f"select count({ID}) from {COURSE} where {ID} = {course_id}"
    # c_count = first_row_first_col(query)
    #
    # if not m_count:
    #     response = make_general_response(MADRASSA_NOT_FOUND, "MadrassaID not found")
    #     return response, OK
    #
    # if not s_count:
    #     response = make_general_response(SHIFT_NOT_FOUND, "ShiftID not found")
    #     return response, OK
    #
    # if not c_count:
    #     response = make_general_response(COURSE_NOT_FOUND, "CourseID not found")
    #     return response, OK
    #
    # query = f"select count({ID}) from {SHIFT_MADRASSA} where {MADRASSA_ID} = {madrassa_id} and {SHIFT_ID} = {shift_id}"
    # sm_count = first_row_first_col(query)
    #
    # query = f"select count({ID}) from {SHIFT_COURSE} where {COURSE_ID} = {course_id} and {SHIFT_ID} = {shift_id}"
    # sc_count = first_row_first_col(query)
    #
    # r = False
    # if not sm_count:
    #     index = select_max(SHIFT_MADRASSA) + 1
    #     query = f"insert into {SHIFT_MADRASSA}({ID},{SHIFT_ID},{MADRASSA_ID}) values({index},{shift_id},{madrassa_id})"
    #     r = insert_query(query)
    #
    # if r or sm_count:
    #     query = f"select distinct {SHIFT_ID},{SHIFT_NAME},{START_TIME},{END_TIME} " \
    #             f"from {SHIFT_MADRASSA} inner join {SHIFT} on " \
    #             f"{SHIFT_MADRASSA}.{SHIFT_ID} = {SHIFT}.{ID} " \
    #             f"where {SHIFT_ID} = {shift_id}"
    #
    #     r = select_query(query)
    #     result = r.fetchall()
    #     shift_object = {
    #         gc.ID: result[0][0],
    #         gc.NAME: result[0][1],
    #         gc.START_TIME: str(result[0][2]),
    #         gc.END_TIME: str(result[0][3])
    #     }
    #
    #     query = f"select distinct {MADRASSA_ID},{MADRASSA_NAME} from " \
    #             f"{SHIFT_MADRASSA} inner join {MADRASSA} " \
    #             f"on {SHIFT_MADRASSA}.{MADRASSA_ID} = {MADRASSA}.{ID} " \
    #             f"where {MADRASSA_ID} = {madrassa_id}"
    #     r = select_query(query)
    #     result = r.fetchall()
    #     madrassa_object = {
    #         gc.ID: result[0][0],
    #         gc.NAME: result[0][1]
    #     }
    #
    #
    # r = False
    # if not sc_count:
    #     index = select_max(SHIFT_COURSE) + 1
    #     query = f"insert into {SHIFT_COURSE}({ID},{SHIFT_ID},{COURSE_ID}) values({index},{shift_id},{course_id})"
    #     r = insert_query(query)
    #
    # if r or sc_count:
    #     query = f"select distinct {SHIFT_ID},{SHIFT_NAME},{START_TIME},{END_TIME} " \
    #             f"from {SHIFT_COURSE} inner join {SHIFT} on " \
    #             f"{SHIFT_COURSE}.{SHIFT_ID} = {SHIFT}.{ID} " \
    #             f"where {SHIFT_ID} = {shift_id}"
    #
    #     r = select_query(query)
    #     result = r.fetchall()
    #     shift_object = {
    #         gc.ID: result[0][0],
    #         gc.NAME: result[0][1],
    #         gc.START_TIME: str(result[0][2]),
    #         gc.END_TIME: str(result[0][3])
    #     }
    #
    #     query = f"select distinct {COURSE_ID},{COURSE_NAME} from " \
    #             f"{SHIFT_COURSE} inner join {COURSE} " \
    #             f"on {SHIFT_COURSE}.{COURSE_ID} = {COURSE}.{ID} " \
    #             f"where {COURSE_ID} = {course_id}"
    #     r = select_query(query)
    #     result = r.fetchall()
    #     course_object = {
    #         gc.ID: result[0][0],
    #         gc.NAME: result[0][1]
    #     }
    #
    # # print('madrassa_object1',madrassa_object)
    # # print('shift_object1',shift_object)
    # # print('shift_object2',shift_object)
    # # print('course_object1', course_object)
    # response = make_general_response(SUCCESS,"Success")
    # response[MADRASSA] = madrassa_object
    # response[SHIFT] = shift_object
    # response[COURSE] = course_object
    # return response, OK


@app.route(GET_MADRASSA_DETAILS, methods=[GET])
@authorize_request
def get_madrassa_details():
    query_params = request.args
    length_query_param = len(query_params)
    if length_query_param == 0:
        response = make_general_response(MISSING_QUERY_PARAM, "Query params are missing")
        return response, BAD_REQUEST

    elif len(query_params) > 1:
        response = make_general_response(ADDITIONAL_QUERY_PARAM, "Additional Query params")
        return response, BAD_REQUEST

    elif not query_params.get(gc.MADRASSA_ID):
        response = make_general_response(INVALID_QUERY_PARAM, "Invalid query params")
        return response, BAD_REQUEST

    madrassa_detail_id = query_params.get(gc.MADRASSA_ID)

    query = f"select * from {MADRASSA_DETAILS} where {gc.ID} = {madrassa_detail_id}"
    r = select_query(query)
    result = r.fetchall()
    shift_id = result[0][0]
    madrassa_id = result[0][1]
    course_id = result[0][2]

    query = f"select distinct {SHIFT_ID},{SHIFT_NAME},{START_TIME},{END_TIME} " \
            f"from {MADRASSA_DETAILS} inner join {SHIFT} on " \
            f"{MADRASSA_DETAILS}.{SHIFT_ID} = {SHIFT}.{ID} " \
            f"where {SHIFT_ID} = {shift_id}"
    r = select_query(query)
    result = r.fetchall()
    shift_object = {
        gc.ID: result[0][0],
        gc.NAME: result[0][1],
        gc.START_TIME: str(result[0][2]),
        gc.END_TIME: str(result[0][3])
    }

    query = f"select distinct {MADRASSA_ID},{MADRASSA_NAME} from " \
            f"{MADRASSA_DETAILS} inner join {MADRASSA} " \
            f"on {MADRASSA_DETAILS}.{MADRASSA_ID} = {MADRASSA}.{ID} " \
            f"where {MADRASSA_ID} = {madrassa_id}"
    r = select_query(query)
    result = r.fetchall()
    madrassa_object = {
        gc.ID: result[0][0],
        gc.NAME: result[0][1]
    }

    query = f"select distinct {COURSE_ID},{COURSE_NAME} from " \
            f"{MADRASSA_DETAILS} inner join {COURSE} " \
            f"on {MADRASSA_DETAILS}.{COURSE_ID} = {COURSE}.{ID} " \
            f"where {COURSE_ID} = {course_id}"
    r = select_query(query)
    result = r.fetchall()
    course_object = {
        gc.ID: result[0][0],
        gc.NAME: result[0][1]
    }

    response = make_general_response(SUCCESS, "SUCCESS")
    response[gc.DATA] = {}
    response[gc.DATA][MADRASSA] = madrassa_object
    response[gc.DATA][SHIFT] = shift_object
    response[gc.DATA][COURSE] = course_object
    return response, OK


@app.route(ADD_USER, methods=[POST])
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

    index = select_max(USER) + 1
    query = f"insert into {USER}({ID},{USER_NAME},{FATHER_NAME},{CNIC},{EMAIl},{MOTHER_TONGUE},{CONTACT}," \
            f"{GENDER_ID},{GUARDIAN_NAME},{GUARDIAN_CONTACT},{DOB},{AGE})" \
            f"values({index},'{name}','{fname}','{cnic}','{email}','{mt}','{contact}',{gender_id}," \
            f"'{guardian_name}','{guardian_contact}','{dob}','{age}')"
    print(query)
    r = insert_query(query)
    if r:
        query = f"select * from {USER} where {ID} = {index}"
        r = select_query(query)
        result = r.fetchall()
        data = {
            gc.ID: result[0][0],
            gc.NAME: result[0][1],
            gc.FATHER_NAME: result[0][2],
            gc.CNIC: result[0][3],
            gc.EMAIL: result[0][4],
            gc.MOTHER_TONGUE: result[0][5],
            gc.CONTACT: result[0][6],
            gc.GENDER_ID: result[0][7],
            gc.GUARDIAN_NAME: result[0][8],
            gc.GUARDIAN_CONTACT: result[0][9],
            gc.DATE_OF_BIRTH: result[0][10],
            gc.AGE: result[0][11],
        }
        response = make_general_response(SUCCESS, "SUCCESS")
        response[gc.DATA] = data
        return response, CREATED

    else:
        response = make_general_response(FAIL, "FAIL")
        return response, BAD_REQUEST







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
