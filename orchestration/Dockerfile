FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install flask requests
EXPOSE 5100
CMD ["python", "orchestrator.py"]
