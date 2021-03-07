from functools import wraps
from jwt import decode
from flask import current_app
from hashlib import sha256

from codes.status_codes import UNAUTHORIZED, BAD_REQUEST
from codes.response_codes import FAIL, MISSING_TOKEN
from constants.table_names import ADMIN
from constants.column_names import USERNAME, PASSWORD
from constants.flask_constants import SECRET_KEY, X_ACCESS_TOKEN
from constants import general_constants as gc
from database_layer.database import select_query
from helper.request_response import request_header, make_general_response


def authorize_request(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        token = None
        headers = request_header()
        if X_ACCESS_TOKEN in headers:
            token = headers[X_ACCESS_TOKEN]
        if not token:
            response = make_general_response(MISSING_TOKEN, 'token is missing')
            return response, UNAUTHORIZED

        # try:
        algorithm = gc.SHA256
        data = decode(token, current_app.config[SECRET_KEY], algorithms=[algorithm])
        query = f"Select {PASSWORD} from {ADMIN} where {USERNAME} = '{data.get(gc.USERNAME)}'"
        r = select_query(query)
        if r:
            result = r.fetchall()
            password = result[0][PASSWORD]
            hashed_password = sha256(password.encode(gc.ASCII)).hexdigest()
            if hashed_password == data.get(gc.PASSWORD):
                return f(*args, **kwargs)
        response = make_general_response(FAIL, 'FAIL')
        return response, BAD_REQUEST
        # except:
        #     response = make_general_response(INVALID_TOKEN, 'token is invalid')
        #     return response, UNAUTHORIZED

    return wrap
