def get_value(key):
    from config.project_config import config
    return config[key]


DEFAULT_ATTENDANCE_STATUS = get_value('DEFAULT_ATTENDANCE_STATUS')
