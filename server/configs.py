from pymongo import MongoClient

Databases = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'exuni_db',
        'USER': 'postgres',
        'PASSWORD': 'slowj504',
        'HOST': 'localhost',
        'PORT': '3030',
        'ATOMIC_REQUESTS': True,
        'TEST': {
            'MIRROR': 'default',
        },
    }

}

client = MongoClient(
    host='localhost',
    port=27017
)

db_handle = client['sobhan_logs']
RequestLogs = db_handle['request_logs']

PEC = {
    'PIN_CODE': "123456",
    'TERMINAL': ""
}

