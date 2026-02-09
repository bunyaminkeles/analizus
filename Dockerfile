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

CMD ["sh", "-c", "bash deploy.sh && gunicorn analizdestek.wsgi:application --bind 0.0.0.0:${PORT:-8000} --access-logfile - --error-logfile -"]
