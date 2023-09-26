rebuild:
	venv/bin/python manage.py migrate
	venv/bin/python manage.py compilemessages -l en
	venv/bin/python manage.py collectstatic --noinput
	systemctl restart hermes

recelery:
	systemctl restart hermes_celery
	systemctl restart hermes_beat
	systemctl restart hermes_flower
	systemctl restart hermes

