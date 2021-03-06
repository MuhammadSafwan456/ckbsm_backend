from constants.table_names import GENDER
from constants.column_names import ID, GENDER
from config.db_column_to_response import mapper
from database_layer import database
from helper.database import select_max
from helper.request_response import map_response
from codes.response_codes import GENDER_NOT_FOUND, SUCCESS, FAIL
from helper.user import find_user_by_gender


def find_gender_by_id(_id):
    query = f"select * from {GENDER} where {ID}={_id}"
    r = database.select_query(query)
    if r:
        result = r.fetchall()
        gender = None
        for i in result:
            gender = map_response(i, mapper)
        return gender
    return None


def delete_gender_by_id(_id):
    query = f'delete from {GENDER} where {ID}={_id}'
    return database.insert_query(query)


def update_gender_by_id(_id, name):
    query = f"update {GENDER} set {GENDER} = '{name}' where id = {_id}"
    return database.insert_query(query)


def insert_gender_by_id(_id, name):
    query = f"insert into {GENDER}({ID},{GENDER}) values({_id},'{name}')"
    return database.insert_query(query)


def get_all_genders():
    query = f"select * from {GENDER}"
    r = database.select_query(query)
    if r:
        result = r.fetchall()
        genders = []
        for i in result:
            mapped_data = map_response(i, mapper)
            genders.append(mapped_data)
        return genders
    return []


def add_new_gender(name):
    max_index = select_max(GENDER)
    if max_index is None:
        return [], FAIL, "FAIL"

    index = max_index + 1
    r = insert_gender_by_id(index, name)
    if r:
        gender = find_gender_by_id(index)
        return gender, SUCCESS, "SUCCESS"
    return [], FAIL, "FAIL"


def update_gender(_id, name):
    gender = find_gender_by_id(_id)
    if gender is None:
        return [], GENDER_NOT_FOUND, "gender Not Found"
    r = update_gender_by_id(_id, name)
    if r:
        gender = find_gender_by_id(_id)
        return gender, SUCCESS, "SUCCESS"
    return [], GENDER_NOT_FOUND, "Already Up to Date"


def delete_gender(_id):
    user_detail = find_user_by_gender(_id)
    if user_detail:
        return False, GENDER_NOT_FOUND, f"Cannot delete genderID {_id}.It is in used somewhere else"
    r = delete_gender_by_id(_id)
    if r:
        return True, SUCCESS, "SUCCESS"
    else:
        return False, GENDER_NOT_FOUND, "gender not found"
