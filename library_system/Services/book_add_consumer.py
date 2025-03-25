import pika
import grpc
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from grpc_proto import library_pb2, library_pb2_grpc

def callback(ch, method, properties, body):
    title, author = body.decode().split(":")
    print(f" Adding book - Title: {title}, Author: {author}")

    with grpc.insecure_channel("book_service:50052") as channel:
        stub = library_pb2_grpc.BookServiceStub(channel)
        response = stub.AddBook(library_pb2.BookRequest(title=title, author=author))
        print(f" Add Book status: {response.message}")

connection = pika.BlockingConnection(pika.ConnectionParameters('host.docker.internal'))
channel = connection.channel()
channel.queue_declare(queue='book_additions')
channel.basic_consume(queue='book_additions', on_message_callback=callback, auto_ack=True)

print(" Waiting for add book tasks. To exit press CTRL+C")
channel.start_consuming()
