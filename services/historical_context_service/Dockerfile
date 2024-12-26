FROM python:3.11-slim

WORKDIR /app

# Copy application code into the container
COPY ./app/ /app/

# Install Flask
RUN pip install flask

# Expose the service port
EXPOSE 5006

# Command to run the application
CMD ["python", "routes.py"]

