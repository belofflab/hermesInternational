rebuild:
	venv/bin/python manage.py migrate
	venv/bin/python manage.py compilemessages -l en
	venv/bin/python manage.py collectstatic --noinput
	systemctl restart hermes

