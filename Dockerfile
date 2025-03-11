# Use official Python image
FROM python:3.9-slim

# Set working directory in the container
WORKDIR /app

# Copy the application files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port on which Flask runs
EXPOSE 8337

# Run the Flask application
CMD ["python", "app.py"]
