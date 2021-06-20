"""
Author : s.aryani456@gmail.com
helper functions related to role
"""


from codes.response_codes import ROLE_NOT_FOUND, SUCCESS, FAIL
from constants.column_names import ID, ROLE_NAME
from constants.table_names import ROLE
from config.db_column_to_response import mapper
from database_layer import database
from helper.database import select_max
from helper.request_response import map_response
from helper.user import find_enrollment_of_role


def find_role_by_id(_id):
    query = f"select * from {ROLE} where {ID}={_id}"
    r = database.select_query(query)
    if r:
        result = r.fetchall()
        role = None
        for i in result:
            role = map_response(i, mapper)
        return role
    return None


def delete_role_by_id(_id):
    query = f'delete from {ROLE} where {ID} ={_id}'
    return database.insert_query(query)


def update_role_by_id(_id, name):
    query = f"update {ROLE} set {ROLE_NAME} = '{name}' where id = {_id}"
    return database.insert_query(query)


def insert_role_by_id(_id, name):
    query = f"insert into {ROLE}({ID}, {ROLE_NAME}) values({_id},'{name}')"
    return database.insert_query(query)


def get_all_roles():
    query = f"select * from {ROLE}"
    r = database.select_query(query)
    if r:
        result = r.fetchall()
        roles = []
        for i in result:
            mapped_data = map_response(i, mapper)
            roles.append(mapped_data)
        return roles
    return []


def add_new_role(name):
    max_index = select_max(ROLE)
    if max_index is None:
        return [], FAIL, "FAIL"
    index = max_index + 1
    r = insert_role_by_id(index, name)
    if r:
        role = find_role_by_id(index)
        return role, SUCCESS, "SUCCESS"
    return [], FAIL, "FAIL"


def update_role(_id, name):
    role = find_role_by_id(_id)
    if role is None:
        return [], ROLE_NOT_FOUND, "Role Not Found"
    r = update_role_by_id(_id, name)
    if r:
        role = find_role_by_id(_id)
        return role, SUCCESS, "SUCCESS"
    return [], ROLE_NOT_FOUND, "Already Up to Date"


def delete_role(_id):
    enrollment = find_enrollment_of_role(_id)
    if enrollment:
        return False, ROLE_NOT_FOUND, f"Cannot delete roleID {_id}.It is in used somewhere else"
    r = delete_role_by_id(_id)
    if r:
        return True, SUCCESS, "SUCCESS"
    return False, ROLE_NOT_FOUND, "ROLE_NOT_FOUND"
