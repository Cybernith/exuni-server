from pymongo import MongoClient

Databases = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'exuni_db',
        'USER': 'postgres',
        'PASSWORD': '58936bf3904894e2a72ff75395401376',
        'HOST': 'dokku-postgres-exuni-db',
        'PORT': '5432',
        'ATOMIC_REQUESTS': True,
        'TEST': {
            'MIRROR': 'default',
        },
    }

}

client = MongoClient(
    'mongodb://exuni-mongo-db:3b30316f2b64e75b2d4d02ca767bb13c@dokku-mongo-exuni-mongo-db:27017/exuni_mongo_db'
)

db_handle = client['sobhan_logs']
RequestLogs = db_handle['request_logs']

PEC = {
    'PIN_CODE': "123456",
    'TERMINAL': ""
}

