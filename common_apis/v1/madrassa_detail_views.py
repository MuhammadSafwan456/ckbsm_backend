from flask import request, Blueprint
from helper.authorization import authorize_request
from helper.request_response import *
from constants.route_constants import *
from constants.flask_constants import *
from codes.status_codes import *
from codes.response_codes import *
from helper.request_response import requires
from helper.madrassa_detail import set_new_madrassa_details, get_madrassa_detail_by_id
from common_apis.v1 import app

madrassa_detail_api = Blueprint("madrassa_detail_api", __name__, url_prefix='')


@madrassa_detail_api.route(SET_MADRASSA_DETAILS, methods=[POST])
@authorize_request
@requires([gc.MADRASSA_ID, gc.SHIFT_ID, gc.COURSE_ID], body=gc.JSON)
def set_madrassa_details():
    request_body = request.get_json()
    data, response_code, detail = set_new_madrassa_details(request_body[gc.SHIFT_ID], request_body[gc.COURSE_ID],
                                                           request_body[gc.MADRASSA_ID])
    response = make_general_response(response_code, detail)
    if data:
        print(f"_____________________{data}")
        response[gc.DATA] = data
        return response, CREATED
    return response, BAD_REQUEST


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


@madrassa_detail_api.route(GET_MADRASSA_DETAILS, methods=[GET])
@authorize_request
@requires([gc.MADRASSA_ID], body=gc.QUERY_PARAMS)
def get_madrassa_details():
    query_params = request.args
    madrassa_detail_id = query_params.get(gc.MADRASSA_ID)
    madrassa_detail = get_madrassa_detail_by_id(madrassa_detail_id)
    if madrassa_detail:
        response = make_general_response(SUCCESS, "Success")
        response[gc.DATA] = madrassa_detail
        return response, OK
    else:
        response = make_general_response(MADRASSA_NOT_FOUND, "Madrassa Details Not found")
        return response, BAD_REQUEST
