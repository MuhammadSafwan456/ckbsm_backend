import re
import datetime


def validate_cnic(cnic):
    result = re.match("^[0-9]{5}-[0-9]{7}-[0-9]$", cnic)
    if result is None:
        return False
    return True


def validate_time(time):
    try:
        if not len(time) == 4:
            return False, None
        hour = time[0:2]
        mint = time[2:4]
        if int(hour) > 23 or int(mint) > 59:
            return False, None
    except:
        return False, None
    return True, time + "00"


def validate_email(email):
    result = re.match("^.+[ @].+[.].+", email)
    if result is None:
        return False
    return True


def validate_contact(number):
    result = re.match("^03[0-4][0-9]-[0-9]{7}", number)
    if result is None:
        return False
    return True


def validate_date(date):
    if not len(date) == 8:
        return False
    yy = date[0:4]
    mm = date[4:6]
    dd = date[6:8]
    try:
        datetime.datetime(int(yy), int(mm), int(dd))
    except ValueError:
        return False
    return True


def verify_param(required, received):
    for req in required:
        if req in received:
            pass
        else:
            return req
    return None

