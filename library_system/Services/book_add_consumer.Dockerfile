FROM python:3.10-slim

WORKDIR /app

# Copy both consumers and the service folder
COPY Services /app/Services
COPY grpc_proto /app/grpc_proto
COPY ./wait-for-rabbit.sh /app/wait-for-rabbit.sh

RUN chmod +x /app/wait-for-rabbit.sh
RUN pip install grpcio grpcio-tools pika

# Default run book_add_consumer.py
CMD ["sh", "/app/wait-for-rabbit.sh", "python", "Services/book_add_consumer.py"]
