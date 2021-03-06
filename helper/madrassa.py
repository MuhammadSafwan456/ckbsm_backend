from constants.table_names import MADRASSA
from constants.column_names import ID, MADRASSA_NAME
from config.db_column_to_response import mapper
from database_layer import database
from helper.database import select_max
from helper.request_response import map_response
from codes.response_codes import MADRASSA_NOT_FOUND, SUCCESS, FAIL


def find_madrassa_by_id(_id):
    query = f"select * from {MADRASSA} where {ID}={_id}"
    r = database.select_query(query)
    if r:
        result = r.fetchall()
        madrassa = None
        for i in result:
            madrassa = map_response(i, mapper)
        return madrassa
    return None


def delete_madrassa_by_id(_id):
    query = f'delete from {MADRASSA} where {ID}={_id}'
    return database.insert_query(query)


def update_madrassa_by_id(_id, name):
    query = f"update {MADRASSA} set {MADRASSA_NAME} = '{name}' where id = {_id}"
    return database.insert_query(query)


def insert_madrassa_by_id(_id, name):
    query = f"insert into {MADRASSA}({ID},{MADRASSA_NAME}) values({_id},'{name}')"
    return database.insert_query(query)


def get_all_madrassas():
    query = f"select * from {MADRASSA}"
    r = database.select_query(query)
    if r:
        result = r.fetchall()
        madrassas = []
        for i in result:
            mapped_data = map_response(i, mapper)
            madrassas.append(mapped_data)
        return madrassas
    return []


def add_new_madrassa(name):
    max_index = select_max(MADRASSA)
    if max_index is None:
        return [], FAIL, "FAIL"

    index = max_index + 1
    r = insert_madrassa_by_id(index, name)
    if r:
        madrassa = find_madrassa_by_id(index)
        return madrassa, SUCCESS, "SUCCESS"
    return [], FAIL, "FAIL"


def update_madrassa(_id, name):
    madrassa = find_madrassa_by_id(_id)
    if madrassa is None:
        return [], MADRASSA_NOT_FOUND, "madrassa Not Found"
    r = update_madrassa_by_id(_id, name)
    if r:
        madrassa = find_madrassa_by_id(_id)
        return madrassa, SUCCESS, "SUCCESS"
    return [], MADRASSA_NOT_FOUND, "Already Up to Date"


def delete_madrassa(_id):
    from helper.madrassa_detail import find_madrassa_detail_by_madrassa_id
    madrassa_detail = find_madrassa_detail_by_madrassa_id(_id)
    if madrassa_detail:
        return False, MADRASSA_NOT_FOUND, f"Cannot delete madrassaID {_id}.It is in used somewhere else"
    r = delete_madrassa_by_id(_id)
    if r:
        return True, SUCCESS, "SUCCESS"
    else:
        return False, MADRASSA_NOT_FOUND, "Madrassa not found"
