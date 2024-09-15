# Use Python 3.9 as the base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the required packages
RUN pip install -r requirements.txt

# Copy the application code
COPY app.py .
COPY init_tasks.py .

# Expose the port the app runs on
EXPOSE 5002

# Run the Flask app
CMD ["python", "app.py"]
