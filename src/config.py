from environs import Env

env = Env()

ORM = {
    'connections': {
        'default': env.str('DB_URL', default='postgres://tim:123@localhost:5432/hack-2021-final'),
    },
    'apps': {
        'core': {
            'models': ['aerich.models', 'models'],
        },
    },
    'use_tz': True,
    'timezone': 'UTC',
}

DEBUG = env.bool('DEBUG', default=False)
LISTEN = env.str('LISTEN', default='0.0.0.0')  # noqa: S104
PORT = env.int('PORT', default=8000)
BROKER = env.str('BROKER_URL', default='redis://localhost:6379/0')
NOMINATIM = env.str('NOMINATIM_URL', default='http://geobase:8080')
