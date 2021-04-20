from fastapi import FastAPI
from pydantic import BaseModel


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
