import grpc


from grpc_proto import auth_pb2, auth_pb2_grpc, library_pb2, library_pb2_grpc
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="supersecretkey")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
def register_user(request: Request, username: str = Form(...), password: str = Form(...)):
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = auth_pb2_grpc.AuthServiceStub(channel)
        response = stub.RegisterUser(auth_pb2.AuthRequest(username=username, password=password))

    if response.success:
        request.session["user"] = username
        return RedirectResponse(url="/books", status_code=302)
    else:
        return {"error": response.message}


@app.post("/login")
def login_user(request: Request, username: str = Form(...), password: str = Form(...)):
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = auth_pb2_grpc.AuthServiceStub(channel)
        response = stub.LoginUser(auth_pb2.AuthRequest(username=username, password=password))

    if response.success:
        request.session["user"] = username
        return RedirectResponse(url="/books", status_code=303)
    return {"error": response.message}

@app.get("/books", response_class=HTMLResponse)
def books_page(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/register")

    with grpc.insecure_channel("localhost:50052") as channel:
        stub = library_pb2_grpc.BookServiceStub(channel)
        response = stub.GetBooks(library_pb2.Empty())

    print("DEBUG: Books received in FastAPI:")
    for book in response.books:
        print(f"ID: {book.id}, Title: {book.title}, Author: {book.author}, Available: {book.available}, Reserved By: {book.reserved_by}")

    return templates.TemplateResponse("index.html", {"request": request, "books": response.books, "user": user})


@app.post("/add_book")
def add_book(request: Request, title: str = Form(...), author: str = Form(...)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/register")

    with grpc.insecure_channel("localhost:50052") as channel:
        stub = library_pb2_grpc.BookServiceStub(channel)
        response = stub.AddBook(library_pb2.BookRequest(title=title, author=author))

    if response.success:
        return RedirectResponse(url="/books", status_code=302)
    else:
        return {"error": response.message}


@app.post("/reserve/{book_id}")
def reserve_book(request: Request, book_id: int):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/register")

    with grpc.insecure_channel("localhost:50052") as channel:
        stub = library_pb2_grpc.BookServiceStub(channel)
        response = stub.ReserveBook(library_pb2.ReserveRequest(book_id=book_id, username=user))

    return RedirectResponse(url="/books", status_code=302)

@app.post("/return_book")
def return_book(request: Request, book_id: str = Form(...)):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/register")

    with grpc.insecure_channel("localhost:50052") as channel:
        stub = library_pb2_grpc.BookServiceStub(channel)
        response = stub.ReturnBook(library_pb2.ReturnRequest(book_id=int(book_id), username=user))

    return RedirectResponse(url="/books", status_code=302)
@app.get("/logout")
def logout_user(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)


__all__ = ["app"]
