web: gunicorn analizdestek.wsgi:application --bind 0.0.0.0:$PORT
release: python manage.py migrate forum 0028 --fake && python manage.py migrate && python manage.py setup_categories && python manage.py create_badges && python manage.py populate_skills && python manage.py import_quiz
