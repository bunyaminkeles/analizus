#!/bin/bash
# Render build script

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🔄 Running migrations..."
python manage.py migrate --noinput

echo "🔧 Verifying critical database tables..."
python manage.py shell -c "
from django.db import connection
from django.core.management import call_command

tables = connection.introspection.table_names()
to_fix = [
    ('yoktez', 'yoktez_yoktezsearchjob'),
]
for app, table in to_fix:
    if table not in tables:
        print(f'[FIX] Table {table} missing — resetting {app} migration state...')
        call_command('migrate', app, 'zero', fake=True, verbosity=0)
        call_command('migrate', app, verbosity=1)
    else:
        print(f'[OK]  {table}')
"

echo "🧹 Cleaning up old database records (Neon capacity management)..."
python manage.py cleanup_database

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "👤 Creating/updating superuser..."
python manage.py create_admin

echo "✅ Build complete!"
