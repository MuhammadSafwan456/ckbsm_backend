from constants.table_names import MADRASSA_DETAILS
from constants.column_names import ID, SHIFT_ID, COURSE_ID
from config.db_column_to_response import mapper
from database_layer.database import select_query
from helper.request_response import map_response


def find_madrassa_detail_by_id(_id):
    query = f"select * from {MADRASSA_DETAILS} where {ID}={_id}"
    r = select_query(query)
    if r:
        result = r.fetchall()
        madrassa_detail = None
        for i in result:
            madrassa_detail = map_response(i, mapper)
        return madrassa_detail
    return None


def find_madrassa_detail_by_shift_id(shift_id):
    query = f"select * from {MADRASSA_DETAILS} where {SHIFT_ID}={shift_id}"
    r = select_query(query)
    if r:
        result = r.fetchall()
        madrassa_detail = None
        for i in result:
            madrassa_detail = map_response(i, mapper)
        return madrassa_detail
    return None


def find_madrassa_detail_by_course_id(course_id):
    query = f"select * from {MADRASSA_DETAILS} where {COURSE_ID}={course_id}"
    r = select_query(query)
    if r:
        result = r.fetchall()
        madrassa_detail = None
        for i in result:
            madrassa_detail = map_response(i, mapper)
        return madrassa_detail
    return None
