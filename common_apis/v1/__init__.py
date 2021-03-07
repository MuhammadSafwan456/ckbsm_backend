# import libraries
from flask import Flask, app
from hashlib import sha256
from flask_apscheduler import APScheduler

# local imports
from common_apis.v1.attendance_views import attendance_api
from common_apis.v1.course_views import course_api
from common_apis.v1.gender_views import gender_api
from common_apis.v1.login_views import login_api
from common_apis.v1.madrassa_detail_views import madrassa_detail_api
from common_apis.v1.madrassa_views import madrassa_api
from common_apis.v1.role_views import role_api
from common_apis.v1.shift_views import shift_api
from common_apis.v1.user_views import user_api
from config.app_config import JWT_SECRET_KEY
from constants.flask_constants import DEBUG, SECRET_KEY
from constants.general_constants import ASCII
from cron_jobs.cron_add_attendance_record_for_all_enrollment import cron_add_attendance_record_for_all_enrollments

add_attendance_scheduler = APScheduler()

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
    add_attendance_scheduler.add_job(id='add_attendance_scheduler', func=cron_add_attendance_record_for_all_enrollments,
                                     trigger='interval', seconds=24, start_date='01:00:00')
    add_attendance_scheduler.start()
    app.run()
