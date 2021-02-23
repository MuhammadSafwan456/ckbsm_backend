from constants.table_names import ROLE
from constants.column_names import ID
from config.db_column_to_response import mapper
from database_layer.database import select_query
from helper.response import map_response


def find_role_by_id(_id):
    query = f"select * from {ROLE} where {ID}={_id}"
    r = select_query(query)
    result = r.fetchall()
    role = None
    for i in result:
        role = map_response(i, mapper)
    return role