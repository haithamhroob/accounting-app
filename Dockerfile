# ── Stage 1: Base image ──────────────────────────────────────────────────────
FROM python:3.11-slim

# Set environment variables
# Prevents Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /app

# Install system dependencies needed by psycopg2 (PostgreSQL driver)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (Docker caching optimization)
# If requirements.txt hasn't changed, Docker won't re-install packages
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the project files into the container
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose the port the app will run on
EXPOSE 8000

# Start the app using Gunicorn (production-grade WSGI server)
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]
