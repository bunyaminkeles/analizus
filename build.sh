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

echo "📚 Adding missing content to empty categories..."
python manage.py add_missing_content

echo "🏆 Creating badges and updating ranks..."
python manage.py create_badges

echo "🎯 Creating skills..."
python manage.py create_skills

echo "📝 Importing quiz questions..."
python manage.py import_quiz

echo "✅ Build complete!"
