import grpc
from concurrent import futures

import sqlite3
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from grpc_proto import library_pb2, library_pb2_grpc

# Database setup
conn = sqlite3.connect("library.db", check_same_thread=False, isolation_level=None)
cursor = conn.cursor()
cursor.execute("PRAGMA journal_mode=WAL;")
cursor.execute("PRAGMA synchronous=NORMAL;")

# Create Books Table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        available INTEGER DEFAULT 1,
        reserved_by TEXT DEFAULT NULL
    )
""")
conn.commit()

class BookService(library_pb2_grpc.BookServiceServicer):
    def AddBook(self, request, context):
        cursor.execute("INSERT INTO books (title, author, available) VALUES (?, ?, 1)",
                       (request.title, request.author))
        conn.commit()
        return library_pb2.BookResponse(success=True, message="Book added successfully")

    def ReserveBook(self, request, context):
        print(f"DEBUG: Reserving book {request.book_id} for user {request.username}")  # ✅ Debugging

        cursor.execute("SELECT reserved_by FROM books WHERE id=?", (request.book_id,))
        existing = cursor.fetchone()

        if existing and existing[0]:  # ✅ If book is already reserved
            return library_pb2.BookResponse(success=False, message="Book is already reserved")

        cursor.execute("UPDATE books SET available=0, reserved_by=? WHERE id=? AND available=1",
                       (request.username, request.book_id))
        conn.commit()

        print(f"DEBUG: Updated reserved_by field in DB: {request.username}")  # ✅ Debugging
        return library_pb2.BookResponse(success=True, message="Book reserved successfully")
    def GetBooks(self, request, context):
        cursor.execute("SELECT id, title, author, available, reserved_by FROM books")  # ✅ Add reserved_by
        books = cursor.fetchall()

        print(f"DEBUG: Retrieved books from database: {books}")  # ✅ Debugging

        books_list = [library_pb2.Book(id=row[0], title=row[1], author=row[2], available=row[3], reserved_by=row[4] if row[4] else "" ) for row in books]
        return library_pb2.BookList(books=books_list)
    def ReturnBook(self, request, context):
        print(f"DEBUG: Returning book {request.book_id} for user {request.username}")  # ✅ Debugging

        cursor.execute("SELECT reserved_by FROM books WHERE id=?", (request.book_id,))
        book = cursor.fetchone()

        if not book or book[0] != request.username:
            return library_pb2.BookResponse(success=False, message="You cannot return this book.")

        cursor.execute("UPDATE books SET available=1, reserved_by=NULL WHERE id=?", (request.book_id,))
        conn.commit()

        print(f"DEBUG: Book {request.book_id} returned successfully")  # ✅ Debugging
        return library_pb2.BookResponse(success=True, message="Book returned successfully")



def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    library_pb2_grpc.add_BookServiceServicer_to_server(BookService(), server)
    server.add_insecure_port("[::]:50052")
    print("Listening on port 50052")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
