from constants.table_names import USER, ENROLLMENT
from constants.column_names import ID, USER_ID, ROLE_ID, MADRASSA_DETAIL_ID, ENROLLMENT_DATE
import constants.general_constants as gc
from config.db_column_to_response import mapper
from database_layer.database import select_query, insert_query
from helper.request_response import map_response
from helper.database import select_max
from codes.response_codes import USER_ALREADY_ENROLLED, SUCCESS, FAIL


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


def enroll_user_in_madrassa(user, madrassa_detail, role, enrollment_date):
    if user_already_enrolled(user, madrassa_detail, role):
        return False, USER_ALREADY_ENROLLED

    _id = select_max(ENROLLMENT) + 1

    query = f"insert into {ENROLLMENT}({ID},{ENROLLMENT_DATE},{USER_ID},{ROLE_ID},{MADRASSA_DETAIL_ID}) " \
            f"values({_id},'{enrollment_date}',{user[gc.ID]},{role[gc.ID]},{madrassa_detail[gc.ID]})"
    print(query)
    inserted = insert_query(query)
    if inserted:
        return True, SUCCESS
    return False, FAIL


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
