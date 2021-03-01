from constants.table_names import ROLE
from constants.column_names import ID, ROLE_NAME
from config.db_column_to_response import mapper
from database_layer import database
from helper.database import select_max
from helper.request_response import map_response
from codes.response_codes import ROLE_NOT_FOUND, SUCCESS, FAIL
from helper.user import find_enrollment_of_role


def get_all_roles():
    query = f"select * from {ROLE}"
    r = database.select_query(query)
    result = r.fetchall()
    roles = []
    for i in result:
        mapped_data = map_response(i, mapper)
        roles.append(mapped_data)
    return roles


def add_new_role(name):
    index = select_max(ROLE) + 1
    query = f"insert into {ROLE}({ID}, {ROLE_NAME}) values({index},'{name}')"
    r = database.insert_query(query)
    if r:
        role = find_role_by_id(index)
        return role, SUCCESS, "SUCCESS"
    return [], FAIL, "FAIL"


def find_role_by_id(_id):
    query = f"select * from {ROLE} where {ID}={_id}"
    r = database.select_query(query)
    result = r.fetchall()
    role = None
    for i in result:
        role = map_response(i, mapper)
    return role


def update_role(_id, name):
    role = find_role_by_id(_id)
    if role is None:
        return [], ROLE_NOT_FOUND, "Role Not Found"

    query = f"update {ROLE} set {ROLE_NAME} = '{name}' where id = {_id}"
    r = database.insert_query(query)
    if r:
        role = find_role_by_id(_id)
        return role, SUCCESS, "SUCCESS"
    else:
        return [], ROLE_NOT_FOUND, "Already Up to Date"


def delete_role(_id):
    enrollment = find_enrollment_of_role(_id)
    if enrollment:
        return False, ROLE_NOT_FOUND, f"Cannot delete roleID {_id}.It is in used somewhere else"

    query = f'delete from {ROLE} where {ID} ={_id}'
    r = database.insert_query(query)
    if r:
        return True, SUCCESS, "SUCCESS"

    else:
        return False, ROLE_NOT_FOUND, "ROLE_NOT_FOUND"
