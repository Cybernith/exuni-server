from pymongo import MongoClient

Databases = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'exuni_db',
        'USER': 'postgres',
        'PASSWORD': '3bac126a292bf85ba4248a2d59a258a8',
        'HOST': 'dokku-postgres-exuni-db',
        'PORT': '5432',
        'ATOMIC_REQUESTS': True,
        'TEST': {
            'MIRROR': 'default',
        },
    }

}

client = MongoClient(
    'mongodb://exuni-mongo-db:59a98e7b7269f9242021c5615163f586@dokku-mongo-exuni-mongo-db:27017/exuni_mongo_db'
)

db_handle = client['sobhan_logs']
RequestLogs = db_handle['request_logs']

PEC = {
    'PIN_CODE': "123456",
    'TERMINAL': ""
}

