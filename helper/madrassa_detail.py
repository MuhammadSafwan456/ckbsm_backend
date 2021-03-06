from codes.response_codes import SHIFT_NOT_FOUND, COURSE_NOT_FOUND, MADRASSA_NOT_FOUND, ALREADY_EXIST, SUCCESS, FAIL
from constants.table_names import MADRASSA_DETAILS, MADRASSA, SHIFT, COURSE
from constants.column_names import ID, SHIFT_ID, COURSE_ID, MADRASSA_ID
from constants import general_constants as gc
from config.db_column_to_response import mapper
from database_layer import database
from helper.request_response import map_response
from helper.shift import find_shift_by_id
from helper.course import find_course_by_id
from helper.madrassa import find_madrassa_by_id
from helper.database import select_max


def find_madrassa_detail_by_id(_id):
    query = f"select * from {MADRASSA_DETAILS} where {ID}={_id}"
    r = database.select_query(query)
    if r:
        result = r.fetchall()
        madrassa_detail = None
        for i in result:
            madrassa_detail = map_response(i, mapper)
        return madrassa_detail
    return None


def find_madrassa_detail_by_shift_id(shift_id):
    query = f"select * from {MADRASSA_DETAILS} where {SHIFT_ID}={shift_id}"
    r = database.select_query(query)
    if r:
        result = r.fetchall()
        madrassa_detail = None
        for i in result:
            madrassa_detail = map_response(i, mapper)
        return madrassa_detail
    return None


def find_madrassa_detail_by_course_id(course_id):
    query = f"select * from {MADRASSA_DETAILS} where {COURSE_ID}={course_id}"
    r = database.select_query(query)
    if r:
        result = r.fetchall()
        madrassa_detail = None
        for i in result:
            madrassa_detail = map_response(i, mapper)
        return madrassa_detail
    return None


def find_madrassa_detail_by_madrassa_id(madrassa_id):
    query = f"select * from {MADRASSA_DETAILS} where {MADRASSA_ID}={madrassa_id}"
    r = database.select_query(query)
    if r:
        result = r.fetchall()
        madrassa_detail = None
        for i in result:
            madrassa_detail = map_response(i, mapper)
        return madrassa_detail
    return None


def find_madrassa_detail_by_shift_course_madrassa(shift_id, course_id, madrassa_id):
    query = f"select * from {MADRASSA_DETAILS} where " \
            f"{SHIFT_ID}={shift_id} and " \
            f"{MADRASSA_ID}={madrassa_id} and " \
            f"{COURSE_ID}={course_id}"
    r = database.select_query(query)
    if r:
        result = r.fetchall()
        madrassa_detail = None
        for i in result:
            madrassa_detail = map_response(i, mapper)
        return madrassa_detail
    return None


def insert_madrassa_detail_by_id(_id, shift_id, course_id, madrassa_id):
    query = f"insert into {MADRASSA_DETAILS}({ID}, {SHIFT_ID}, {COURSE_ID}, {MADRASSA_ID})" \
            f"values({_id}, {shift_id}, {course_id}, {madrassa_id})"
    return database.insert_query(query)


def set_new_madrassa_details(shift_id, course_id, madrassa_id):
    shift = find_shift_by_id(shift_id)
    if shift is None:
        return [], SHIFT_NOT_FOUND, "Shift Not Found"

    course = find_course_by_id(course_id)
    if course is None:
        return [], COURSE_NOT_FOUND, "Course Not Found"

    madrassa = find_madrassa_by_id(madrassa_id)
    if madrassa is None:
        return [], MADRASSA_NOT_FOUND, "Madrassa Not Found"

    madrassa_detail = find_madrassa_detail_by_shift_course_madrassa(shift_id, course_id, madrassa_id)
    if madrassa_detail:
        return [], ALREADY_EXIST, f"Madrassa_details already exist with id={madrassa_detail[gc.ID]}"

    max_index = select_max(MADRASSA_DETAILS)
    if max_index is None:
        return [], FAIL, "FAIL"

    index = max_index + 1
    r = insert_madrassa_detail_by_id(index, shift_id, course_id, madrassa_id)
    if r:
        data = get_madrassa_detail_by_id(index)
        return data, SUCCESS, "SUCCESS"
    return [], FAIL, "FAIL"


def get_madrassa_detail_by_id(_id):
    madrassa_detail = find_madrassa_detail_by_id(_id)
    if madrassa_detail is None:
        return None

    shift_id = madrassa_detail[gc.SHIFT_ID]
    course_id = madrassa_detail[gc.COURSE_ID]
    madrassa_id = madrassa_detail[gc.MADRASSA_ID]

    shift = find_shift_by_id(shift_id)
    course = find_course_by_id(course_id)
    madrassa = find_madrassa_by_id(madrassa_id)
    data = {
        ID: madrassa_detail[gc.ID],
        SHIFT: shift,
        COURSE: course,
        MADRASSA: madrassa
    }

    return data
