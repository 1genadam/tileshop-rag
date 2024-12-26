FROM python:3.11-slim

WORKDIR /app

# Copy application code and config
COPY . /app/

# Install dependencies
RUN pip install flask requests

# Expose the port
EXPOSE 5100

# Command to run the service
CMD ["python", "orchestrator.py"]
