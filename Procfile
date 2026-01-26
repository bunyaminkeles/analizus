web: daphne -b 0.0.0.0 -p $PORT analizdestek.asgi:application
release: python manage.py migrate && python manage.py setup_categories && python manage.py create_badges && python manage.py populate_skills && python manage.py import_quiz
