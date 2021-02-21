from flask import Flask, app
from constants.flask_constants import *
from hashlib import sha256
from config.app_config import JWT_SECRET_KEY
from constants.general_constants import *

from common_apis.v1.attendance_views import attendance_api
from common_apis.v1.course_views import course_api
from common_apis.v1.gender_views import gender_api
from common_apis.v1.login_views import login_api
from common_apis.v1.madrassa_detail_views import madrassa_detail_api
from common_apis.v1.madrassa_views import madrassa_api
from common_apis.v1.role_views import role_api
from common_apis.v1.shift_views import shift_api
from common_apis.v1.user_views import user_api

app = Flask(__name__)
app.config[DEBUG] = True
app.config[SECRET_KEY] = sha256(JWT_SECRET_KEY.encode(ASCII)).hexdigest()

app.register_blueprint(attendance_api)
app.register_blueprint(course_api)
app.register_blueprint(gender_api)
app.register_blueprint(login_api)
app.register_blueprint(madrassa_detail_api)
app.register_blueprint(madrassa_api)
app.register_blueprint(role_api)
app.register_blueprint(shift_api)
app.register_blueprint(user_api)

if __name__ == '__main__':
    app.run()
