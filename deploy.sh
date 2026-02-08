#!/bin/bash
# Render deployment script

echo "🚀 Deploying to Render..."

# Run migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Load seed content (only if database is empty)
TOPIC_COUNT=$(python manage.py shell -c "from forum.models import Topic; print(Topic.objects.count())" 2>/dev/null | tail -1)

if [ "$TOPIC_COUNT" -eq "0" ]; then
    echo "📚 Database is empty, loading seed content..."
    python manage.py load_seed_content
else
    echo "✓ Database already has $TOPIC_COUNT topics, skipping seed"
fi

# Setup categories, badges, skills (idempotent)
echo "🏷️ Setting up categories, badges, skills..."
python manage.py setup_all --skip-quiz

# Import quiz questions from quiz_soruları/ (duplicate-safe)
echo "🧠 Importing quiz questions..."
python manage.py import_quiz

# Load success stories (only if none exist)
STORY_COUNT=$(python manage.py shell -c "from forum.models import SuccessStory; print(SuccessStory.objects.count())" 2>/dev/null | tail -1)

if [ "$STORY_COUNT" -eq "0" ]; then
    echo "🌟 Loading success stories..."
    python manage.py populate_success_stories
else
    echo "✓ Already has $STORY_COUNT success stories, skipping"
fi

echo "✅ Deployment complete!"
