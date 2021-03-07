def get_value(key):
    from config.project_config import config
    return config[key]


JWT_SECRET_KEY = get_value('JWT_SECRET_KEY')
