from constants import general_constants as gc
from constants.table_names import ATTENDANCE, ATTENDANCE_RECORD
from constants.column_names import ATTENDANCE_DATE, ENROLLMENT_ID, ID, STATUS, STATUS_ID
from database_layer import database
from helper.request_response import map_response
from config.db_column_to_response import mapper
from helper.database import select_max
from config.config import DEFAULT_ATTENDANCE_STATUS


def find_attendance_record_of_enrollment_at_date(enrollment_id, date):
    query = f"select * from {ATTENDANCE_RECORD} where {ENROLLMENT_ID}={enrollment_id} and {ATTENDANCE_DATE} = {date}"
    r = database.select_query(query)
    if r:
        result = r.fetchall()
        attendance = None
        for i in result:
            attendance = map_response(i, mapper)
        return attendance
    return None


def create_attendance_for_enrollment_at_date(enrollment_id, date):
    max_index = select_max(ATTENDANCE_RECORD)
    if max_index is None:
        return False
    index = max_index + 1
    status = find_attendance_status_id_by_name(DEFAULT_ATTENDANCE_STATUS)
    if status is None:
        status = add_new_status(DEFAULT_ATTENDANCE_STATUS)

    if not status:
        return False
    r = insert_attendance_record_by_id(index, date, enrollment_id, status[gc.ID])
    return r


def find_attendance_status_id_by_name(name):
    query = f"select {ID} from {ATTENDANCE} where {STATUS}='{name}'"
    r = database.select_query(query)
    if r:
        result = r.fetchall()
        status_id = None
        for i in result:
            status_id = map_response(i, mapper)
        return status_id
    return None


def add_new_status(status):
    max_index = select_max(ATTENDANCE)
    if max_index is None:
        return False
    index = max_index + 1
    r = insert_new_attendance_status_by_id(index, status)
    if r:
        status = find_attendance_status_id_by_name(status)
        return status
    return False


def insert_new_attendance_status_by_id(_id, status):
    query = f"insert into {ATTENDANCE}({ID},{STATUS}) values ({_id},'{status}')"
    return database.insert_query(query)


def insert_attendance_record_by_id(_id, date, enrollment_id, status_id):
    query = f"insert into {ATTENDANCE_RECORD}({ID},{ATTENDANCE_DATE},{ENROLLMENT_ID},{STATUS_ID}) values ({_id},{date},{enrollment_id},{status_id})"
    return database.insert_query(query)
