from flask import request, jsonify, Blueprint
from helper.authorization import authorize_request
from helper.response import *
from helper.validate import *
from helper.database import *
from config.db_column_to_response import mapper
from constants.route_constants import *
from constants.flask_constants import *
from constants.table_names import *
from constants.column_names import *
from database_layer.database import select_query, insert_query
from codes.status_codes import *
from codes.response_codes import *

attendance_api = Blueprint("attendance_api", __name__, url_prefix='')


@attendance_api.route(USER_ATTENDANCE, methods=[POST])
@authorize_request
def user_attendance():
    return jsonify({request.base_url: request.method})


@attendance_api.route(BULK_USER_ATTENDANCE, methods=[POST])
@authorize_request
def bulk_user_attendance():
    return jsonify({request.base_url: request.method})


@attendance_api.route(GET_ALL_ATTENDANCE, methods=[GET])
@authorize_request
def get_all_attendance():
    return jsonify({request.base_url: request.method})
