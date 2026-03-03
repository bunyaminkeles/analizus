#!/bin/bash
# Render build script

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🔄 Running migrations..."
python manage.py migrate --noinput

echo "🔧 Checking yoktez table..."
python -c "
import django, os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'analizdestek.settings')
django.setup()
from django.db import connection
tables = connection.introspection.table_names()
if 'yoktez_yoktezsearchjob' not in tables:
    print('[MISSING] yoktez_yoktezsearchjob')
    sys.exit(1)
else:
    print('[OK] yoktez_yoktezsearchjob')
    sys.exit(0)
" || (
    echo "Fixing yoktez migration..."
    python manage.py migrate yoktez zero --fake
    python manage.py migrate yoktez
    echo "yoktez migration fixed."
)

echo "🧹 Cleaning up old database records (Neon capacity management)..."
python manage.py cleanup_database

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "👤 Creating/updating superuser..."
python manage.py create_admin

echo "✅ Build complete!"
