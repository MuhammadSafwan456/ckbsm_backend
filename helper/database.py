from database_layer.database import select_query
from constants.column_names import *


def select_max(table):
    query = f'select max({ID}) as {ID} from {table}'
    r = select_query(query)
    if r:
        result = r.fetchall()
        if result[0].get(ID):
            return result[0].get(ID)
        return 0
    return None

