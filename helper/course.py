from codes.response_codes import COURSE_NOT_FOUND, SUCCESS, FAIL
from constants.column_names import ID, COURSE_NAME
from constants.table_names import COURSE
from config.db_column_to_response import mapper
from database_layer import database
from helper.database import select_max
from helper.request_response import map_response


def find_course_by_id(_id):
    query = f"select * from {COURSE} where {ID}={_id}"
    r = database.select_query(query)
    if r:
        result = r.fetchall()
        course = None
        for i in result:
            course = map_response(i, mapper)
        return course
    return None


def delete_course_by_id(_id):
    query = f'delete from {COURSE} where {ID} = {_id}'
    return database.insert_query(query)


def update_course_by_id(_id, name):
    query = f"update {COURSE} set {COURSE_NAME} = '{name}' where {ID} = {_id}"
    return database.insert_query(query)


def insert_course_by_id(_id, name):
    query = f"insert into {COURSE}({ID},{COURSE_NAME}) values({_id},'{name}')"
    return database.insert_query(query)


def get_all_courses():
    query = f"select * from {COURSE}"
    r = database.select_query(query)
    if r:
        result = r.fetchall()
        courses = []
        for i in result:
            mapped_data = map_response(i, mapper)
            courses.append(mapped_data)
        return courses
    return []


def add_new_course(name):
    max_index = select_max(COURSE)
    if max_index is None:
        return [], FAIL, "FAIL"

    index = max_index + 1
    r = insert_course_by_id(index, name)
    if r:
        course = find_course_by_id(index)
        return course, SUCCESS, "SUCCESS"
    return [], FAIL, "FAIL"


def update_course(_id, name):
    course = find_course_by_id(_id)
    if course is None:
        return [], COURSE_NOT_FOUND, "Course Not Found"
    r = update_course_by_id(_id, name)
    if r:
        course = find_course_by_id(_id)
        return course, SUCCESS, "SUCCESS"
    return [], COURSE_NOT_FOUND, "Already Up to Date"


def delete_course(_id):
    from helper.madrassa_detail import find_madrassa_detail_by_course_id
    madrassa_detail = find_madrassa_detail_by_course_id(_id)
    if madrassa_detail:
        return False, COURSE_NOT_FOUND, f"Cannot delete courseID {_id}.It is in used somewhere else"
    r = delete_course_by_id(_id)
    if r:
        return True, SUCCESS, "SUCCESS"
    else:
        return False, COURSE_NOT_FOUND, "Course not found"
