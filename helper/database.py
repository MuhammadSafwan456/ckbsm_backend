"""
Author : s.aryani456@gmail.com
helper functions related to DB
"""


from constants.column_names import ID
from database_layer.database import select_query


def select_max(table):
    query = f'select max({ID}) as {ID} from {table}'
    r = select_query(query)
    if r:
        result = r.fetchall()
        if result[0].get(ID):
            return result[0].get(ID)
        return 0
    return None
