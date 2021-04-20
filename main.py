import hashlib
from fastapi import FastAPI, Response
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta


app = FastAPI()
app.counter = 0
app.patient_counter = 0
app.patient_list = []


class HelloResp(BaseModel):
    msg: str


class Patient(BaseModel):
    name: str
    surname: str


class SavePatient(BaseModel):
    id: int
    name: str
    surname: str
    register_date: str
    vaccination_date: str


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


@app.post("/register", response_model=SavePatient, status_code=201)
def patient_register(patient: Patient):
    app.patient_counter += 1
    today = datetime.now().strftime("%Y-%m-%d")
    register_day = str(today)
    len_letters = len([i for i in patient.name + patient.surname if i.isalpha()])
    vaccination_day = (datetime.now() + timedelta(days=len_letters)).strftime('%Y-%m-%d')
    new_patient = SavePatient(
        id=app.patient_counter,
        name=patient.name,
        surname=patient.surname,
        register_date=register_day,
        vaccination_date=vaccination_day,
    )
    app.patient_list.append(new_patient)
    return new_patient


@app.get("/patient/{id}", response_model=SavePatient)
def patient(id: int):
    if id < 1:
        return Response(status_code=400)
    elif id > len(app.patient_list):
        return Response(status_code=404)
    else:
        Response(status_code=200)
        return app.patient_list[id - 1].dict()
