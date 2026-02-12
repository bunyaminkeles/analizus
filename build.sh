#!/bin/bash
# Render build script

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🔄 Running migrations..."
python manage.py migrate --noinput

echo "🧹 Cleaning up old database records (Neon capacity management)..."
python manage.py cleanup_database

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "👤 Creating/updating superuser..."
python manage.py create_admin

echo "✅ Build complete!"
