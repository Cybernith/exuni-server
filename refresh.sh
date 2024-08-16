source ~/Env/sh/bin/activate
rm db.sqlite3
python manage.py migrate
python manage.py loaddata ./fixtures/*