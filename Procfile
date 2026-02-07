release: python manage.py migrate && python manage.py collectstatic --noinput && python manage.py setup_admin
web: gunicorn core.wsgi
