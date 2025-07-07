# Use an official Python runtime as a parent image
FROM python:3.8.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TORCH_HOME=/usr/src/exuni/.torch_cache
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
RUN pip install -r requirements.txt



# Copy project
COPY . .
#COPY .env .
# COPY ./start.sh .
# COPY./celery.sh .

