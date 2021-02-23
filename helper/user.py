from constants.table_names import USER
from constants.column_names import ID
from config.db_column_to_response import mapper
from database_layer.database import select_query
from helper.response import map_response


def find_user_by_id(_id):
    query = f"select * from {USER} where {ID}={_id}"
    r = select_query(query)
    result = r.fetchall()
    user = None
    for i in result:
        user = map_response(i, mapper)
    return user

def enroll_user_in_madrassa(user,madrassa_detail,enrollment_date):
    query = f""
