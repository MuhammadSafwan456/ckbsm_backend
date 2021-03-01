from constants.table_names import SHIFT
from constants.column_names import ID, SHIFT_NAME,START_TIME,END_TIME
from config.db_column_to_response import mapper
from database_layer import database
from helper.database import select_max
from helper.request_response import map_response
from codes.response_codes import SHIFT_NOT_FOUND, SUCCESS, FAIL
from helper.madrassa_detail import find_madrassa_detail_by_shift_id
# from helper.user import find_enrollment_of_role


def get_all_shifts():
    query = f"select * from {SHIFT}"
    r = database.select_query(query)
    if r:
        result = r.fetchall()
        roles = []
        for i in result:
            mapped_data = map_response(i, mapper)
            roles.append(mapped_data)
        return roles
    return []


def add_new_shift(name,start_time, end_time):
    index = select_max(SHIFT) + 1
    query = f"insert into shift(id,shift_name,start_time,end_time) " \
            f"values({index},'{name}','{start_time}','{end_time}')"
    r = database.insert_query(query)

    if r:
        shift = find_shift_by_id(index)
        return shift, SUCCESS, "SUCCESS"
    return [], FAIL, "FAIL"


def find_shift_by_id(_id):
    query = f"select * from {SHIFT} where {ID}={_id}"
    r = database.select_query(query)
    if r:
        result = r.fetchall()
        role = None
        for i in result:
            role = map_response(i, mapper)
        return role
    return None


def update_shift(_id, name,start_time, end_time):
    shift = find_shift_by_id(_id)
    if shift is None:
        return [], SHIFT_NOT_FOUND, "Shift Not Found"

    query = f"update {SHIFT} " \
            f"set {SHIFT_NAME} = '{name}' , {START_TIME} = '{start_time}', {END_TIME}= '{end_time}' " \
            f"where {ID} = {_id} "
    r = database.insert_query(query)
    if r:
        shift = find_shift_by_id(_id)
        return shift, SUCCESS, "SUCCESS"
    return [], SHIFT_NOT_FOUND, "Already Up to Date"


def delete_shift(_id):
    madrassa_detail = find_madrassa_detail_by_shift_id(_id)
    if madrassa_detail:
        return False, SHIFT_NOT_FOUND, f"Cannot delete shiftID {_id}.It is in used somewhere else"

    query = f'delete from {SHIFT} where {ID} ={_id}'
    r = database.insert_query(query)
    if r:
        return True, SUCCESS, "SUCCESS"

    else:
        return False, SHIFT_NOT_FOUND, "ROLE_NOT_FOUND"
