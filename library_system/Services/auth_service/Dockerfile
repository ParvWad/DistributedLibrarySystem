FROM python:3.10-slim

WORKDIR /app

COPY Services/auth_service /app
COPY grpc_proto /app/grpc_proto

RUN pip install grpcio grpcio-tools passlib[bcrypt]

EXPOSE 50051

CMD ["python", "auth_service.py"]
