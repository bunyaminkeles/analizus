FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

ENV CHROME_BINARY_PATH=/usr/bin/chromium

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py setup_categories && python manage.py create_badges && python manage.py populate_skills && python manage.py import_quiz && daphne -b 0.0.0.0 -p ${PORT:-8000} analizdestek.asgi:application"]
