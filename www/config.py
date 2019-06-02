config_override = {
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
        'secret': 'COOKIE_KEY_wr4sw4rqka25f'
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
