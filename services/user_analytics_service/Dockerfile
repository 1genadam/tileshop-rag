FROM python:3.11-slim

WORKDIR /app

# Copy application code
COPY ./app /app

# Install dependencies
RUN pip install flask

# Expose the port for the service
EXPOSE 5105

# Command to run the service
CMD ["python", "routes.py"]
