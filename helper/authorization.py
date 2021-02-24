from functools import wraps
from helper.request_response import make_general_response
from codes.status_codes import *
from codes.response_codes import *
import constants.general_constants as gc
from constants.table_names import *
from constants.column_names import *
from database_layer.database import select_query
from constants.flask_constants import *
from hashlib import sha256
import jwt
from flask import request, current_app


def authorize_request(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        token = None
        if X_ACCESS_TOKEN in request.headers:
            token = request.headers[X_ACCESS_TOKEN]
        if not token:
            response = make_general_response(MISSING_TOKEN, 'token is missing')
            return response, UNAUTHORIZED

        # try:
        algorithm = gc.SHA256
        data = jwt.decode(token, current_app.config[SECRET_KEY], algorithms=[algorithm])
        query = f"Select {PASSWORD} from {ADMIN} where {USERNAME} = '{data.get(gc.USERNAME)}'"
        r = select_query(query)
        result = r.fetchall()
        password = result[0][PASSWORD]
        hashed_password = sha256(password.encode(gc.ASCII)).hexdigest()
        if hashed_password == data.get(gc.PASSWORD):
            return f(*args, **kwargs)
        # except:
        #     response = make_general_response(INVALID_TOKEN, 'token is invalid')
        #     return response, UNAUTHORIZED

    return wrap
