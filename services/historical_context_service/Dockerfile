FROM python:3.11-slim
WORKDIR /app
COPY app/ .
RUN pip install flask requests
EXPOSE 5106
CMD ["python", "routes.py"]
