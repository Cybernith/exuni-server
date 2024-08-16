from pymongo import MongoClient

Databases = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'ATOMIC_REQUESTS': True
    }
}

client = MongoClient(
    host='localhost',
    port=27017
)
db_handle = client['sobhan_logs']
RequestLogs = db_handle['request_logs']

"""
    Gateways
"""

PEC = {
    'PIN_CODE': "",
    'TERMINAL': ""
}
