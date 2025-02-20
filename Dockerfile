# Use the official Python 3.12 image as the base image
FROM python:3.12-slim

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set the working directory inside the container
WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the init.sql file into the container
COPY ./app/init.sql /app/init.sql

# Copy the src directory into the container
# Copy the src directory to /app/
COPY ./docker.sh /app/

COPY . /app/ 

RUN chmod +x /app/docker.sh


CMD [ "/app/docker.sh" ]