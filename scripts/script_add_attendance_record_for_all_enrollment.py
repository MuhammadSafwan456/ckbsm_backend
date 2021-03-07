from helper.validate import validate_date
from helper.user import find_all_enrollments
from helper.attendance import find_attendance_record_of_enrollment_at_date, create_attendance_for_enrollment_at_date
from constants import general_constants as gc


def run():
    recorded_already_present = []
    record_created = []
    record_not_created = []
    while True:
        date = input("Enter date(YYYYMMDD) for which you want to create attendance record: ")
        if not validate_date(date):
            continue
        enrollments = find_all_enrollments()
        if enrollments is None:
            print("No enrollments found")
            break
        for enrollment in enrollments:
            attendance = find_attendance_record_of_enrollment_at_date(enrollment[gc.ID], date)
            if attendance is None:
                created = create_attendance_for_enrollment_at_date(enrollment[gc.ID], date)
                if created:
                    record_created.append(enrollment[gc.ID])
                else:
                    record_not_created.append(enrollment[gc.ID])
            else:
                recorded_already_present.append(enrollment[gc.ID])

        print("recorded_already_present for enrollment ID", recorded_already_present, "at date ", date)
        print("record_created for enrollment ID", record_created, "at date ", date)
        print("record_not_created for enrollment ID", record_not_created, "at date ", date)
        break


if __name__ == "__main__":
    run()
