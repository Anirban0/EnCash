FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=encash.settings.prod

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Apply migrations (which also seed the default categories) then serve.
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn encash.wsgi:application --bind 0.0.0.0:8000 --workers 3"]
