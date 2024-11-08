# Dockerfile for cart_service
FROM python:3.9-slim

WORKDIR /app
COPY ./cart_service /app

RUN pip install -r requirements.txt

CMD ["python", "cart_service.py"]
