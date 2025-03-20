import grpc
from concurrent import futures
import sqlite3
from passlib.context import CryptContext
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from grpc_proto import auth_pb2, auth_pb2_grpc

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

conn = sqlite3.connect("library.db", check_same_thread=False, isolation_level=None)
cursor = conn.cursor()
cursor.execute("PRAGMA journal_mode=WAL;")
cursor.execute("PRAGMA synchronous=NORMAL;")

# Create Users Table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
""")
conn.commit()

class AuthService(auth_pb2_grpc.AuthServiceServicer):
    def RegisterUser(self, request, context):
        hashed_password = pwd_context.hash(request.password)
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (request.username, hashed_password))
            conn.commit()
            return auth_pb2.AuthResponse(success=True, message="User registered successfully")
        except sqlite3.IntegrityError:
            return auth_pb2.AuthResponse(success=False, message="Username already exists")

    def LoginUser(self, request, context):
        cursor.execute("SELECT * FROM users WHERE username=?", (request.username,))
        user = cursor.fetchone()
        if not user or not pwd_context.verify(request.password, user[2]):
            return auth_pb2.AuthResponse(success=False, message="Invalid credentials")
        return auth_pb2.AuthResponse(success=True, message="Login successful")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_pb2_grpc.add_AuthServiceServicer_to_server(AuthService(), server)
    server.add_insecure_port("[::]:50051")
    print("✅ Auth Service is running on port 50051...")  # ✅ Add this
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
