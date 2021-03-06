from flask import request, Blueprint
from helper.authorization import authorize_request
from helper.request_response import *
from config.db_column_to_response import mapper
from constants.route_constants import *
from constants.flask_constants import *
from constants.table_names import *
from constants.column_names import *
from database_layer.database import select_query, insert_query
from codes.status_codes import *
from codes.response_codes import *
from helper.course import get_all_courses, add_new_course, update_course, delete_course
from common_apis.v1 import app
from helper.request_response import requires

course_api = Blueprint("course_api", __name__, url_prefix='')


@course_api.route(GET_COURSES, methods=[GET])
@authorize_request
def get_course():
    courses = get_all_courses()
    if courses:
        response = make_general_response(SUCCESS, "Success")
        response[gc.DATA] = courses
        return response, OK
    else:
        response = make_general_response(FAIL, "FAIL")
        return response, BAD_REQUEST


@course_api.route(ADD_COURSES, methods=[POST])
@authorize_request
@requires([gc.NAME], body=gc.JSON)
def add_courses():
    request_body = request.get_json()
    data, response_code, detail = add_new_course(request_body[gc.NAME])
    response = make_general_response(response_code, detail)
    if data:
        response[gc.DATA] = data
        return response, CREATED
    return response, BAD_REQUEST


@course_api.route(UPDATE_COURSES, methods=[PUT])
@authorize_request
@requires([gc.ID, gc.NAME], body=gc.JSON)
def update_courses():
    request_body = request.get_json()

    data, response_code, detail = update_course(request_body[gc.ID], request_body[gc.NAME])
    response = make_general_response(response_code, detail)
    if data:
        response[gc.DATA] = data
        return response, OK
    return response, BAD_REQUEST

    query = f"update {COURSE} set {COURSE_NAME} = '{request_body[gc.NAME]}' where {ID} = {request_body[gc.ID]}"
    r = insert_query(query)
    if r:
        query = f"select * from {COURSE} where {ID} = {request_body[ID]}"

        r = select_query(query)
        result = r.fetchall()

        for i in result:
            data = map_response(i, mapper)

        response = make_general_response(SUCCESS, "SUCCESS")
        response[gc.DATA] = data
        return response, CREATED

    else:
        response = make_general_response(COURSE_NOT_FOUND, "CourseID not found or Already Updated")
        return response, OK


@course_api.route(DELETE_COURSES, methods=[DELETE])
@authorize_request
@requires([gc.ID], body=gc.QUERY_PARAMS)
def delete_courses():
    query_params = request.args
    deleted, code, detail = delete_course(query_params[gc.ID])
    response = make_general_response(code, detail)
    response[gc.DELETED] = deleted
    if deleted:
        return response, OK
    return response, BAD_REQUEST
