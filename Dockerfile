# Use an official Python runtime as a parent image
FROM python:3.8.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /usr/src/exuni
RUN apt update && apt install gcc



RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    libc-dev \
    netcat-traditional \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*


RUN pip install --upgrade pip
COPY ./requirements.txt .
COPY ./torob_requirements.txt .
RUN pip install --default-timeout=100 -r requirements.txt
RUN pip install -r torob_requirements.txt


# Expose port for dokku/nginx
EXPOSE 5000

# Default command (dokku will override with Procfile if exists)
CMD ["gunicorn", "server.wsgi:application", "--bind", "0.0.0.0:5000", "--workers=3", "--timeout=60", "--keep-alive=60"]


# Copy project
COPY . .
#COPY .env .
# COPY ./start.sh .
# COPY./celery.sh .
