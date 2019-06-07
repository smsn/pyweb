config_override = {
    # 'debug': False,
    'database': {
        'host': '127.0.0.1'
    }
}


config_default = {
    'debug': True,
    'database': {
        'user': 'pyweb',
        'password': 'pyweb',
        'db': 'pyweb_db',
        'host': 'localhost',
        "port": 3306
    },
    'session': {
        'secret_key': 'COOKIE_KEY_wr4sw4rqka25f',
        'cookie_name': 'COOKIE_NAME_pyweb'
    }
}


def merge(default, override):
    configs = {}
    for key, value in default.items():
        if key in override:
            if isinstance(value, dict):
                configs[key] = merge(value, override[key])
            else:
                configs[key] = override[key]
        else:
            configs[key] = value
    return configs


configs = merge(config_default, config_override)
