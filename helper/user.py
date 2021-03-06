from constants.table_names import USER, ENROLLMENT
from constants.column_names import ID, USER_ID, ROLE_ID, MADRASSA_DETAIL_ID, ENROLLMENT_DATE, GENDER_ID, USER_NAME, \
    FATHER_NAME, CNIC, EMAIL, MOTHER_TONGUE, CONTACT, GUARDIAN_NAME, GUARDIAN_CONTACT, DOB, AGE
from codes.response_codes import GENDER_NOT_FOUND
import constants.general_constants as gc
from config.db_column_to_response import mapper
from database_layer.database import select_query, insert_query
from helper.request_response import map_response
from helper.database import select_max
from codes.response_codes import USER_ALREADY_ENROLLED, SUCCESS, FAIL
from database_layer import database


def user_already_enrolled(user, madrassa_detail, role):
    query = f"select * from {ENROLLMENT} where " \
            f"{USER_ID}={user[gc.ID]} and " \
            f"{ROLE_ID}={role[gc.ID]} and " \
            f"{MADRASSA_DETAIL_ID}={madrassa_detail[gc.ID]}"
    print(query)
    r = select_query(query)
    if r:
        result = r.fetchall()
        print(result)
        enrollment = None
        for i in result:
            enrollment = map_response(i, mapper)

        return enrollment is not None
    return True


def find_user_by_id(_id):
    query = f"select * from {USER} where {ID}={_id}"
    r = select_query(query)
    if r:
        result = r.fetchall()
        user = None
        for i in result:
            user = map_response(i, mapper)
        return user
    return None


def find_user_by_gender(gender_id):
    query = f"select * from {USER} where {GENDER_ID}={gender_id}"
    r = select_query(query)
    if r:
        result = r.fetchall()
        user = None
        for i in result:
            user = map_response(i, mapper)
        return user
    return None


def find_enrollment_of_role(role_id):
    query = f"select * from {ENROLLMENT} where {ROLE_ID}={role_id}"
    r = select_query(query)
    if r:
        result = r.fetchall()
        enrollment = None
        for i in result:
            enrollment = map_response(i, mapper)
        return enrollment
    return None


def find_user_by_cnic_or_contact(cnic, contact):
    where_clause = ""

    if cnic or contact:
        where_clause = where_clause + "where"
    if cnic:
        where_clause = where_clause + f" {CNIC}='{cnic}' "
        if contact:
            where_clause = where_clause + "and"
    if contact:
        where_clause = where_clause + f" ({CONTACT}='{contact}' or {GUARDIAN_CONTACT}='{contact}')"
    query = f"select * from {USER} " + where_clause
    print(query)
    r = database.select_query(query)
    if r:
        result = r.fetchall()
        data = []
        for i in result:
            data.append(map_response(i, mapper))
        return data
    return None


def enroll_user_in_madrassa_by_id(_id, user, madrassa_detail, role, enrollment_date):
    query = f"insert into {ENROLLMENT}({ID},{ENROLLMENT_DATE},{USER_ID},{ROLE_ID},{MADRASSA_DETAIL_ID}) " \
            f"values({_id},'{enrollment_date}',{user[gc.ID]},{role[gc.ID]},{madrassa_detail[gc.ID]})"
    return database.insert_query(query)


def enroll_user_in_madrassa(user, madrassa_detail, role, enrollment_date):
    if user_already_enrolled(user, madrassa_detail, role):
        return False, USER_ALREADY_ENROLLED, "User Already enrolled"

    max_index = select_max(ENROLLMENT)
    if max_index is None:
        return [], FAIL, "FAIL"

    index = select_max(ENROLLMENT) + 1
    r = enroll_user_in_madrassa_by_id(index, user, madrassa_detail, role, enrollment_date)
    if r:
        return r, SUCCESS, "Success"
    return r, FAIL, "Fail"


def insert_user_by_id(_id, user):
    query = f"insert into {USER}({ID},{USER_NAME},{FATHER_NAME},{CNIC},{EMAIL},{MOTHER_TONGUE},{CONTACT}," \
            f"{GENDER_ID},{GUARDIAN_NAME},{GUARDIAN_CONTACT},{DOB},{AGE})" \
            f"values({_id},'{user[gc.NAME]}','{user[gc.FATHER_NAME]}','{user[gc.CNIC]}','{user[gc.EMAIL]}'," \
            f"'{user[gc.MOTHER_TONGUE]}','{user[gc.CONTACT]}',{user[gc.GENDER_ID]}," \
            f"'{user[gc.GUARDIAN_NAME]}','{user[gc.GUARDIAN_CONTACT]}','{user[gc.DATE_OF_BIRTH]}','{user[gc.AGE]}')"
    return database.insert_query(query)


def add_new_user(user):
    # importing here due to circular import error

    from helper.gender import find_gender_by_id
    gender = find_gender_by_id(user[gc.GENDER_ID])
    if gender is None:
        return [], GENDER_NOT_FOUND, "gender Not Found"

    max_index = select_max(USER)
    if max_index is None:
        return [], FAIL, "FAIL"

    index = max_index + 1
    r = insert_user_by_id(index, user)
    if r:
        user = find_user_by_id(index)
        return user, SUCCESS, "SUCCESS"
    return [], FAIL, "FAIL"
