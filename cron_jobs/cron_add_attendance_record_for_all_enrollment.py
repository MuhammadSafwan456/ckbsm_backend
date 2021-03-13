from datetime import datetime

from helper.user import find_all_enrollments
from helper.attendance import find_attendance_record_of_enrollment_at_date, create_attendance_for_enrollment_at_date
from constants import general_constants as gc
from config.config import PUBLIC_HOLIDAYS


def cron_add_attendance_record_for_all_enrollments():
    date = datetime.today().strftime('%d-%m')
    if date in PUBLIC_HOLIDAYS:
        return
    else:
        date = datetime.today().strftime('%Y%m%d')

    enrollments = find_all_enrollments()
    for enrollment in enrollments:
        attendance = find_attendance_record_of_enrollment_at_date(enrollment[gc.ID], date)
        if attendance is None:
            create_attendance_for_enrollment_at_date(enrollment[gc.ID], date)


if __name__ == '__main__':
    cron_add_attendance_record_for_all_enrollments()
