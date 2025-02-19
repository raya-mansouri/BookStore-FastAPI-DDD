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
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the .env file into the container
# Copy the .env file to /app/.env/
COPY .env .  

# Copy the src directory into the container
# Copy the src directory to /app/
COPY ./src /app  

# Copy the init.sql file into the container
COPY init.sql /app/init.sql

# Expose the port your FastAPI app will run on
EXPOSE 8000

RUN chmod +x docker.sh
CMD [ "./docker.sh" ]
# Command to run the FastAPI app using Uvicorn
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]