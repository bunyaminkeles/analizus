#!/bin/bash
# Render deployment script

echo "🚀 Deploying to Render..."

# Run migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Load seed content (only if database is empty)
TOPIC_COUNT=$(python manage.py shell -c "from forum.models import Topic; print(Topic.objects.count())" 2>&1 | grep -oE '^[0-9]+$' | tail -1)

if [ -n "$TOPIC_COUNT" ] && [ "$TOPIC_COUNT" -gt "0" ]; then
    echo "✓ Database already has $TOPIC_COUNT topics, skipping seed"
else
    echo "📚 Database is empty, loading seed content..."
    python manage.py load_seed_content
fi

# Setup categories, badges, skills (only if no categories exist)
CATEGORY_COUNT=$(python manage.py shell -c "from forum.models import Category; print(Category.objects.count())" 2>&1 | grep -oE '^[0-9]+$' | tail -1)

if [ -n "$CATEGORY_COUNT" ] && [ "$CATEGORY_COUNT" -gt "0" ]; then
    echo "✓ Already has $CATEGORY_COUNT categories, skipping setup_all"
else
    echo "🏷️ Setting up categories, badges, skills..."
    python manage.py setup_all --skip-quiz
fi

# Import quiz questions (only if not already loaded)
QUIZ_COUNT=$(python manage.py shell -c "from forum.models import QuizQuestion; print(QuizQuestion.objects.count())" 2>&1 | grep -oE '^[0-9]+$' | tail -1)

if [ -n "$QUIZ_COUNT" ] && [ "$QUIZ_COUNT" -gt "0" ]; then
    echo "✓ Already has $QUIZ_COUNT quiz questions, skipping import"
else
    echo "🧠 Importing quiz questions..."
    python manage.py import_quiz
fi

# Load success stories (only if none exist)
STORY_COUNT=$(python manage.py shell -c "from forum.models import SuccessStory; print(SuccessStory.objects.count())" 2>&1 | grep -oE '^[0-9]+$' | tail -1)

if [ -n "$STORY_COUNT" ] && [ "$STORY_COUNT" -gt "0" ]; then
    echo "✓ Already has $STORY_COUNT success stories, skipping"
else
    echo "🌟 Loading success stories..."
    python manage.py populate_success_stories
fi

echo "✅ Deployment complete!"
