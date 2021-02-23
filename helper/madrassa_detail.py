from constants.table_names import MADRASSA_DETAILS
from constants.column_names import ID
from config.db_column_to_response import mapper
from database_layer.database import select_query
from helper.response import map_response


def find_madrassa_detail_by_id(_id):
    query = f"select * from {MADRASSA_DETAILS} where {ID}={_id}"
    r = select_query(query)
    result = r.fetchall()
    madrassa_detail = None
    for i in result:
        madrassa_detail = map_response(i, mapper)
    return madrassa_detail
