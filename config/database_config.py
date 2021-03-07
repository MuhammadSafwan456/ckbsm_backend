def get_value(key):
    from config.project_config import config
    return config[key]


DB_USERNAME = get_value('DB_USERNAME')
DB_PASSWORD = get_value('DB_PASSWORD')
DB_HOST = get_value('DB_HOST')
DB_NAME = get_value('DB_NAME')
