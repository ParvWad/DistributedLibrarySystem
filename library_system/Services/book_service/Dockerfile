FROM python:3.10-slim

WORKDIR /app

# Copy both consumers and the service folder
COPY Services /app/Services
COPY grpc_proto /app/grpc_proto

RUN pip install grpcio grpcio-tools pika

# Default run book_consumer.py (override with book_add_consumer.py in docker-compose)
CMD ["python", "Services/book_consumer.py"]
