import pika
import grpc
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from grpc_proto import library_pb2, library_pb2_grpc

def callback(ch, method, properties, body):
    message = body.decode()
    book_id, username = message.split(":")
    print(f" Received reservation task - Book ID: {book_id}, Username: {username}")

    with grpc.insecure_channel("book_service:50052") as channel:
        stub = library_pb2_grpc.BookServiceStub(channel)
        response = stub.ReserveBook(library_pb2.ReserveRequest(book_id=int(book_id), username=username))
        print(f" Book reservation status: {response.message}")

connection = pika.BlockingConnection(pika.ConnectionParameters('host.docker.internal'))
channel = connection.channel()
channel.queue_declare(queue='book_reservations')

channel.basic_consume(queue='book_reservations', on_message_callback=callback, auto_ack=True)

print("Waiting for reservation tasks. To exit press CTRL+C")
channel.start_consuming()
