import hashlib

from fastapi import FastAPI, Response
from pydantic import BaseModel
from typing import Optional


app = FastAPI()
app.counter = 0


class HelloResp(BaseModel):
    msg: str


@app.get('/')
def root():
    return{'message': "Hello world!"}


@app.get('/hello/{name}', response_model=HelloResp)
def hello_name_view(name: str):
    return HelloResp(msg=f"Hello {name}")


@app.get('/counter')
def counter():
    app.counter += 1
    return str(app.counter)


@app.get("/method", status_code=200)
def give_method():
    return {"method": "GET"}


@app.put("/method", status_code=200)
def give_method():
    return {"method": "PUT"}


@app.options("/method", status_code=200)
def give_method():
    return {"method": "OPTIONS"}


@app.delete("/method", status_code=200)
def give_method():
    return {"method": "DELETE"}


@app.post("/method", status_code=201)
def give_method():
    return {"method": "POST"}


@app.get("/auth", status_code=401)
def auth(password: Optional[str] = None, password_hash: Optional[str] = None):
    if password:
        password = password.encode('utf8')
        haslo = hashlib.sha512(password)
        if haslo.hexdigest() == password_hash:
            return Response(status_code=204)
        else:
            return Response(status_code=401)
    return Response(status_code=401)
