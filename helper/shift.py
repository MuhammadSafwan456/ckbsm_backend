"""
Author : s.aryani456@gmail.com
helper functions related to shift
"""


from codes.response_codes import SHIFT_NOT_FOUND, SUCCESS, FAIL
from constants.table_names import SHIFT
from constants.column_names import ID, SHIFT_NAME, START_TIME, END_TIME
from config.db_column_to_response import mapper
from database_layer import database
from helper.database import select_max
from helper.request_response import map_response


def find_shift_by_id(_id):
    query = f"select * from {SHIFT} where {ID}={_id}"
    r = database.select_query(query)
    if r:
        result = r.fetchall()
        shift = None
        for i in result:
            shift = map_response(i, mapper)
        return shift
    return None


def delete_shift_by_id(_id):
    query = f'delete from {SHIFT} where {ID} ={_id}'
    return database.insert_query(query)


def update_shift_by_id(_id, name, start_time, end_time):
    query = f"update {SHIFT} " \
            f"set {SHIFT_NAME} = '{name}' , {START_TIME} = '{start_time}', {END_TIME}= '{end_time}' " \
            f"where {ID} = {_id} "
    return database.insert_query(query)


def insert_shift_by_id(_id, name, start_time, end_time):
    query = f"insert into shift({ID},{SHIFT_NAME},{START_TIME},{END_TIME}) " \
            f"values({_id},'{name}','{start_time}','{end_time}')"
    return database.insert_query(query)


def get_all_shifts():
    query = f"select * from {SHIFT}"
    r = database.select_query(query)
    if r:
        result = r.fetchall()
        shifts = []
        for i in result:
            mapped_data = map_response(i, mapper)
            shifts.append(mapped_data)
        return shifts
    return []


def add_new_shift(name, start_time, end_time):
    max_index = select_max(SHIFT)
    if max_index is None:
        return [], FAIL, "FAIL"

    index = max_index + 1
    r = insert_shift_by_id(index, name, start_time, end_time)
    if r:
        shift = find_shift_by_id(index)
        return shift, SUCCESS, "SUCCESS"
    return [], FAIL, "FAIL"


def update_shift(_id, name, start_time, end_time):
    shift = find_shift_by_id(_id)
    if shift is None:
        return [], SHIFT_NOT_FOUND, "Shift Not Found"
    r = update_shift_by_id(_id, name, start_time, end_time)
    if r:
        shift = find_shift_by_id(_id)
        return shift, SUCCESS, "SUCCESS"
    return [], SHIFT_NOT_FOUND, "Already Up to Date"


def delete_shift(_id):
    from helper.madrassa_detail import find_madrassa_detail_by_shift_id
    madrassa_detail = find_madrassa_detail_by_shift_id(_id)
    if madrassa_detail:
        return False, SHIFT_NOT_FOUND, f"Cannot delete shiftID {_id}.It is in used somewhere else"
    r = delete_shift_by_id(_id)
    if r:
        return True, SUCCESS, "SUCCESS"

    else:
        return False, SHIFT_NOT_FOUND, "SHIFT_NOT_FOUND"
