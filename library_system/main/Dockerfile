FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better Docker caching
COPY /requirements.txt /app/requirements.txt

# Install everything from requirements.txt
RUN pip install -r /app/requirements.txt

# Copy the rest of the application code
COPY main /app/main
COPY grpc_proto /app/grpc_proto
COPY ./Services /app/Services
COPY ./templates /app/templates


EXPOSE 8000

CMD ["uvicorn", "main.main:app", "--host", "0.0.0.0", "--port", "8000"]
