"""
Author : s.aryani456@gmail.com
helper functions related to attendance
"""


from config.config import DEFAULT_ATTENDANCE_STATUS
from config.db_column_to_response import mapper
from constants import general_constants as gc
from constants.column_names import ATTENDANCE_DATE, ENROLLMENT_ID, ID, STATUS, STATUS_ID
from constants.table_names import ATTENDANCE, ATTENDANCE_RECORD
from database_layer import database
from helper.request_response import map_response
from helper.database import select_max
from codes.response_codes import FAIL,SUCCESS,ATTENDANCE_ALREADY_MARKED


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


def mark_attendance_for_enrollment_at_date(enrollment_id, date, status_id):

    attendance = find_attendance_record_of_enrollment_at_date(enrollment_id,date)
    _id = attendance[gc.ID]
    r = update_attendance_record_by_id(_id, date, enrollment_id, status_id)
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


def find_attendance_status_by_id(_id):
    query = f"select * from {ATTENDANCE} where {ID}='{_id}'"
    r = database.select_query(query)
    if r:
        result = r.fetchall()
        status = None
        for i in result:
            status = map_response(i, mapper)
        return status
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


def update_attendance_record_by_id(_id, date, enrollment_id, status_id):
    query = f"update {ATTENDANCE_RECORD} " \
            f"set {ATTENDANCE_DATE} = '{date}', " \
            f"{ENROLLMENT_ID} = '{enrollment_id}', " \
            f"{STATUS_ID} ='{status_id}' " \
            f"where {ID} = {_id}"
    return database.insert_query(query)


def mark_attendance(enrollment_id, date, status_id):
    attendance = find_attendance_record_of_enrollment_at_date(enrollment_id, date)
    if attendance is None:
        created = create_attendance_for_enrollment_at_date(enrollment_id, date)
        if not created:
            return False, FAIL, "Fail"

    r = mark_attendance_for_enrollment_at_date(enrollment_id, date, status_id)
    if r:
        return r, SUCCESS, "Success"
    return r, ATTENDANCE_ALREADY_MARKED, "Attendance Alreday marked"
