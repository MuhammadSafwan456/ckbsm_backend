from constants.flask_constants import *
from constants.table_names import *
from constants.route_constants import *
from codes.status_codes import *
from codes.response_codes import *
from constants.general_constants import *
from flask import request
from database_layer.database import select_query, insert_query
import flask

app = flask.Flask(__name__)
app.config[DEBUG] = True


def select_max(table):
    query = f'select max(id) from {table}'
    r = select_query(query)
    result = r.fetchall()
    print("________________IN SELECT MAX RESULT _________-", result[0][0])
    if result[0][0]:
        return result[0][0]
    return 0


def make_general_response(code, detail):
    response = {
        RESPONSE_CODE: code,
        RESPONSE_DETAIL: detail
    }
    return response


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
        response = make_general_response(PARAMETER_MISSING, missing + " is missing")
        return response, BAD_REQUEST

    query = f"Select * from admin where username = '{request_body.get(USERNAME)}' and password = '{request_body.get(PASSWORD)}' "
    r = select_query(query)
    result = r.fetchall()
    if len(result) != 0:
        if result[0][0] == request_body.get(USERNAME) and result[0][1] == request_body.get(PASSWORD):
            response = make_general_response(SUCCESS, "SUCCESS")
            return response, OK
        else:
            response = make_general_response(ADMIN_NOT_FOUND, "Incorrect Credentials")
            return response, OK
    else:
        response = make_general_response(ADMIN_NOT_FOUND, "Incorrect Credentials")
        return response, OK


@app.route(ADMIN_DASHBOARD, methods=[GET])
def admin_dashboard():
    def first_row_first_col(query):
        res = select_query(query)
        res = res.fetchall()
        count = res[0][0]
        return count

    query_params = request.args
    length_query_param = len(query_params)
    # admin = request.args.get(ADMIN)
    if length_query_param == 0:
        response = make_general_response(MISSING_QUERY_PARAM, "Query params are missing")
        return response, BAD_REQUEST

    elif len(query_params) > 1:
        response = make_general_response(ADDITIONAL_QUERY_PARAM, "Additional Query params")
        return response, BAD_REQUEST

    elif not query_params.get(ADMIN):
        response = make_general_response(INVALID_QUERY_PARAM, "Invalid query params")
        return response, BAD_REQUEST

    username = query_params.get(ADMIN)
    query = f"Select username from admin where username = '{username}' "
    print(query)
    r = select_query(query)
    result = r.fetchall()
    if len(result) == 0:
        response = make_general_response(ADMIN_NOT_FOUND, "Admin not found")
        return response, OK

    query = "select count(id) from madrassa"
    madrassa_count = first_row_first_col(query)

    query = "select count(id) from course"
    course_count = first_row_first_col(query)

    query = "select count(id) from shift"
    shift_count = first_row_first_col(query)

    query = "select count(id) from enrollment where role_id = 0"
    teacher_count = first_row_first_col(query)

    query = "select count(id) from enrollment where role_id = 1"
    student_count = first_row_first_col(query)

    response = make_general_response(SUCCESS, "Success")
    response[DATA] = {
        'totalStudents': student_count,
        'totalTeachers': teacher_count,
        'totalShifts': shift_count,
        'totalCourses': course_count,
        'totalMadrassas': madrassa_count
    }
    return response, OK


@app.route(GET_ROLES, methods=[GET])
def get_roles():
    query = "select * from role"
    r = select_query(query)
    result = r.fetchall()
    data = []
    for i in result:
        data.append({
            ID: i[0],
            NAME: i[1]
        })

    response = make_general_response(SUCCESS, "Success")
    response[DATA] = data
    return response, OK


@app.route(ADD_ROLES, methods=[POST])
def add_roles():
    request_body = request.get_json()
    missing = verify_param([NAME], request_body)
    if missing:
        response = make_general_response(PARAMETER_MISSING, missing + " is missing")
        return response, BAD_REQUEST
    index = select_max(ROLE) + 1

    query = f"insert into role(id,role_name) values({index},'{request_body[NAME]}')"
    r = insert_query(query)
    if r:
        print("......................  WAH BCCCCC")
        query = f"select * from role where id = {index}"
        r = select_query(query)
        result = r.fetchall()
        data = {
            ID: result[0][0],
            NAME: result[0][1]
        }
        response = make_general_response(SUCCESS, "SUCCESS")
        response[DATA] = data
        return response, CREATED

    else:
        response = make_general_response(FAIL, "FAIL")
        return response, OK


@app.route(UPDATE_ROLES, methods=[PUT])
def update_roles():
    request_body = request.get_json()
    missing = verify_param([ID, NAME], request_body)
    if missing:
        response = make_general_response(PARAMETER_MISSING, missing + " is missing")
        return response, BAD_REQUEST

    query = f"update role set role_name = '{request_body[NAME]}' where id = {request_body[ID]}"
    r = insert_query(query)
    if r:
        print("......................  WAH BCCCCC")
        query = f"select * from role where id = {request_body[ID]}"
        r = select_query(query)
        result = r.fetchall()
        data = {
            ID: result[0][0],
            NAME: result[0][1]
        }
        response = make_general_response(SUCCESS, "SUCCESS")
        response[DATA] = data
        return response, CREATED

    else:
        response = make_general_response(ROLE_NOT_FOUND, "RoleID not found")
        return response, OK


@app.route(DELETE_ROLES, methods=[DELETE])
def delete_roles():
    query_params = request.args
    length_query_param = len(query_params)
    if length_query_param == 0:
        response = make_general_response(MISSING_QUERY_PARAM, "Query params are missing")
        return response, BAD_REQUEST

    elif len(query_params) > 2:
        response = make_general_response(ADDITIONAL_QUERY_PARAM, "Additional Query params")
        return response, BAD_REQUEST

    elif not query_params.get(ID):
        response = make_general_response(INVALID_QUERY_PARAM, "Invalid query params")
        return response, BAD_REQUEST

    query = f'delete from role where id={query_params[ID]}'
    r = insert_query(query)
    if r:
        print("......................  WAH BCCCCC")
        response = make_general_response(SUCCESS, "SUCCESS")
        response[DELETED] = r
        return response, CREATED

    else:
        response = make_general_response(ROLE_NOT_FOUND, "RoleID not found")
        response[DELETED] = r
        return response, OK


@app.route(GET_SHIFTS, methods=[GET])
def get_shifts():
    query = "select * from shift"
    r = select_query(query)
    result = r.fetchall()
    data = []
    for i in result:
        data.append({
            ID: i[0],
            NAME: i[1],
            START_TIME: str(i[2]),
            END_TIME: str(i[3])
        })

    response = make_general_response(SUCCESS, "Success")
    response[DATA] = data
    return response, OK


@app.route(ADD_SHIFT, methods=[POST])
def add_shifts():
    request_body = request.get_json()
    missing = verify_param([NAME, START_TIME, END_TIME], request_body)
    if missing:
        response = make_general_response(PARAMETER_MISSING, missing + " is missing")
        return response, BAD_REQUEST
    index = select_max(SHIFT) + 1

    query = f"insert into shift(id,shift_name,start_time,end_time) " \
            f"values({index},'{request_body[NAME]}','{request_body[START_TIME]}','{request_body[END_TIME]}')"
    r = insert_query(query)
    if r:
        print("......................  WAH BCCCCC")
        query = f"select * from shift where id = {index}"
        r = select_query(query)
        result = r.fetchall()
        data = {
            ID: result[0][0],
            NAME: result[0][1],
            START_TIME: str(result[0][2]),
            END_TIME: str(result[0][3]),
        }
        response = make_general_response(SUCCESS, "SUCCESS")
        response[DATA] = data
        return response, CREATED

    else:
        response = make_general_response(FAIL, "FAIL")
        return response, OK

    # return flask.jsonify({flask.request.base_url: flask.request.method})


@app.route(UPDATE_SHIFT, methods=[PUT])
def update_shifts():
    request_body = request.get_json()
    missing = verify_param([ID, NAME, START_TIME, END_TIME], request_body)
    if missing:
        response = make_general_response(PARAMETER_MISSING, missing + " is missing")
        return response, BAD_REQUEST

    query = f"update shift" \
            f" set shift_name = '{request_body[NAME]}' , start_time = '{request_body[START_TIME]}', " \
            f"end_time= '{request_body[END_TIME]}' where id = {request_body[ID]}"
    print(query)
    r = insert_query(query)
    if r:
        print("......................  WAH BCCCCC")
        query = f"select * from shift where id = {request_body[ID]}"
        r = select_query(query)
        result = r.fetchall()
        data = {
            ID: result[0][0],
            NAME: result[0][1],
            START_TIME: str(result[0][2]),
            END_TIME: str(result[0][3]),
        }
        response = make_general_response(SUCCESS, "SUCCESS")
        response[DATA] = data
        return response, CREATED

    else:
        response = make_general_response(SHIFT_NOT_FOUND, "ShiftID not found")
        return response, OK
    # return flask.jsonify({flask.request.base_url: flask.request.method})


@app.route(DELETE_SHIFTS, methods=[DELETE])
def delete_shifts():
    query_params = request.args
    length_query_param = len(query_params)
    if length_query_param == 0:
        response = make_general_response(MISSING_QUERY_PARAM, "Query params are missing")
        return response, BAD_REQUEST

    elif len(query_params) > 2:
        response = make_general_response(ADDITIONAL_QUERY_PARAM, "Additional Query params")
        return response, BAD_REQUEST

    elif not query_params.get(ID):
        response = make_general_response(INVALID_QUERY_PARAM, "Invalid query params")
        return response, BAD_REQUEST

    query = f'delete from shift where id={query_params[ID]}'
    r = insert_query(query)
    if r:
        print("......................  WAH BCCCCC")
        response = make_general_response(SUCCESS, "SUCCESS")
        response[DELETED] = r
        return response, CREATED

    else:
        response = make_general_response(SHIFT_NOT_FOUND, "ShiftID not found")
        response[DELETED] = r
        return response, OK

    # return flask.jsonify({flask.request.base_url: flask.request.method})


@app.route(GET_COURSES, methods=[GET])
def get_course():
    query = "select * from course"
    r = select_query(query)
    result = r.fetchall()
    data = []
    for i in result:
        data.append({
            ID: i[0],
            NAME: i[1]
        })

    response = make_general_response(SUCCESS, "Success")
    response[DATA] = data
    return response, OK


@app.route(ADD_COURSES, methods=[POST])
def add_courses():
    request_body = request.get_json()
    missing = verify_param([NAME], request_body)
    if missing:
        response = make_general_response(PARAMETER_MISSING, missing + " is missing")
        return response, BAD_REQUEST
    index = select_max(COURSE) + 1

    query = f"insert into course(id,course_name) values({index},'{request_body[NAME]}')"
    r = insert_query(query)
    if r:
        print("......................  WAH BCCCCC")
        query = f"select * from course where id = {index}"
        r = select_query(query)
        result = r.fetchall()
        data = {
            ID: result[0][0],
            NAME: result[0][1]
        }
        response = make_general_response(SUCCESS, "SUCCESS")
        response[DATA] = data
        return response, CREATED

    else:
        response = make_general_response(FAIL, "FAIL")
        return response, OK



@app.route(UPDATE_COURSES, methods=[PUT])
def update_courses():
    request_body = request.get_json()
    missing = verify_param([ID, NAME], request_body)
    if missing:
        response = make_general_response(PARAMETER_MISSING, missing + " is missing")
        return response, BAD_REQUEST

    query = f"update course set course_name = '{request_body[NAME]}' where id = {request_body[ID]}"
    r = insert_query(query)
    if r:
        print("......................  WAH BCCCCC")
        query = f"select * from course where id = {request_body[ID]}"
        r = select_query(query)
        result = r.fetchall()
        data = {
            ID: result[0][0],
            NAME: result[0][1]
        }
        response = make_general_response(SUCCESS, "SUCCESS")
        response[DATA] = data
        return response, CREATED

    else:
        response = make_general_response(COURSE_NOT_FOUND, "CourseID not found")
        return response, OK



@app.route(DELETE_COURSES, methods=[DELETE])
def delete_courses():
    query_params = request.args
    length_query_param = len(query_params)
    if length_query_param == 0:
        response = make_general_response(MISSING_QUERY_PARAM, "Query params are missing")
        return response, BAD_REQUEST

    elif len(query_params) > 2:
        response = make_general_response(ADDITIONAL_QUERY_PARAM, "Additional Query params")
        return response, BAD_REQUEST

    elif not query_params.get(ID):
        response = make_general_response(INVALID_QUERY_PARAM, "Invalid query params")
        return response, BAD_REQUEST

    query = f'delete from course where id={query_params[ID]}'
    r = insert_query(query)
    if r:
        print("......................  WAH BCCCCC")
        response = make_general_response(SUCCESS, "SUCCESS")
        response[DELETED] = r
        return response, CREATED

    else:
        response = make_general_response(COURSE_NOT_FOUND, "CourseID not found")
        response[DELETED] = r
        return response, OK


@app.route(GET_MADRASSAS, methods=[GET])
def get_madrassas():
    query = "select * from madrassa"
    r = select_query(query)
    result = r.fetchall()
    data = []
    for i in result:
        data.append({
            ID: i[0],
            NAME: i[1]
        })

    response = make_general_response(SUCCESS, "Success")
    response[DATA] = data
    return response, OK


@app.route(ADD_MADRASSAS, methods=[POST])
def add_madrassas():
    request_body = request.get_json()
    missing = verify_param([NAME], request_body)
    if missing:
        response = make_general_response(PARAMETER_MISSING, missing + " is missing")
        return response, BAD_REQUEST
    index = select_max(MADRASSA) + 1

    query = f"insert into madrassa(id,madrassa_name) values({index},'{request_body[NAME]}')"
    r = insert_query(query)
    if r:
        print("......................  WAH BCCCCC")
        query = f"select * from madrassa where id = {index}"
        r = select_query(query)
        result = r.fetchall()
        data = {
            ID: result[0][0],
            NAME: result[0][1]
        }
        response = make_general_response(SUCCESS, "SUCCESS")
        response[DATA] = data
        return response, CREATED

    else:
        response = make_general_response(FAIL, "FAIL")
        return response, OK



@app.route(UPDATE_MADRASSAS, methods=[PUT])
def update_madrassas():
    request_body = request.get_json()
    missing = verify_param([ID, NAME], request_body)
    if missing:
        response = make_general_response(PARAMETER_MISSING, missing + " is missing")
        return response, BAD_REQUEST

    query = f"update madrassa set madrassa_name = '{request_body[NAME]}' where id = {request_body[ID]}"
    r = insert_query(query)
    if r:
        print("......................  WAH BCCCCC")
        query = f"select * from madrassa where id = {request_body[ID]}"
        r = select_query(query)
        result = r.fetchall()
        data = {
            ID: result[0][0],
            NAME: result[0][1]
        }
        response = make_general_response(SUCCESS, "SUCCESS")
        response[DATA] = data
        return response, CREATED

    else:
        response = make_general_response(MADRASSA_NOT_FOUND, "MadrassaID not found")
        return response, OK




@app.route(DELETE_MADRASSAS, methods=[DELETE])
def delete_madrassas():
    query_params = request.args
    length_query_param = len(query_params)
    if length_query_param == 0:
        response = make_general_response(MISSING_QUERY_PARAM, "Query params are missing")
        return response, BAD_REQUEST

    elif len(query_params) > 2:
        response = make_general_response(ADDITIONAL_QUERY_PARAM, "Additional Query params")
        return response, BAD_REQUEST

    elif not query_params.get(ID):
        response = make_general_response(INVALID_QUERY_PARAM, "Invalid query params")
        return response, BAD_REQUEST

    query = f'delete from madrassa where id={query_params[ID]}'
    r = insert_query(query)
    if r:
        print("......................  WAH BCCCCC")
        response = make_general_response(SUCCESS, "SUCCESS")
        response[DELETED] = r
        return response, CREATED

    else:
        response = make_general_response(MADRASSA_NOT_FOUND, "MadrassaID not found")
        response[DELETED] = r
        return response, OK


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
