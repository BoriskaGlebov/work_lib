# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV PYTHONPATH=/app


# Expose the port that the app runs on
EXPOSE 5000

# Command to run the application

CMD ["flask", "run", "--host=0.0.0.0"]
#CMD ["flask", "create-admin", "admin"]