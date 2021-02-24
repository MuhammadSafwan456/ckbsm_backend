from constants.table_names import ROLE
from constants.column_names import ID
from config.db_column_to_response import mapper
from database_layer import database
from helper.request_response import map_response


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
    pass

def find_role_by_id(_id):
    query = f"select * from {ROLE} where {ID}={_id}"
    r = select_query(query)
    result = r.fetchall()
    role = None
    for i in result:
        role = map_response(i, mapper)
    return role