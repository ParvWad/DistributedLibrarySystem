#!/bin/sh

# Wait for RabbitMQ to be ready
until nc -z -v -w30 rabbitmq 5672; do
  echo "Waiting for RabbitMQ..."
  sleep 2
done

echo "RabbitMQ is up - executing command"
exec "$@"
