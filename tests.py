from fastapi.testclient import TestClient
from old_app.main import app
import pytest
from datetime import datetime, timedelta

client = TestClient(app)


def test_read_main():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json == {'message': 'Hello World!'}


@pytest.mark.parametrize('name', ['Zenek', 'Marek', 'Alojzy Niezdąży'])
def test_hello_name(name):
    response = client.get(f'/hello/{name}')
    assert response.status_code == 200
    assert response.text == f'"Hello {name}"'


def test_counter(name):
    response = client.get(f"/counter")
    assert response.status_code == 200
    assert response.text == "1"
    # 2nd Try
    response = client.get(f"/counter")
    assert response.status_code == 200
    assert response.text == "2"


def test_methods():
    response = client.get(f"/method")
    assert response.status_code == 200
    assert response.json() == {"method": "GET"}

    response = client.post(f"/method")
    assert response.status_code == 201
    assert response.json() == {"method": "POST"}

    response = client.put(f"/method")
    assert response.status_code == 200
    assert response.json() == {"method": "PUT"}

    response = client.options(f"/method")
    assert response.status_code == 200
    assert response.json() == {"method": "OPTIONS"}

    response = client.delete(f"/method")
    assert response.status_code == 200
    assert response.json() == {"method": "DELETE"}


def test_password():
    response = client.get(
        f"/auth?password=haslo&password_hash=013c6889f799cd986a735118e1888727d1435f7f623d05d58c61bf2cd8b49ac90105e5786"
        f"ceaabd62bbc27336153d0d316b2d13b36804080c44aa6198c533215")
    assert response.status_code == 204

    response = client.get(
        f"/auth?password=haslo&password_hash=f34ad4b3ae1e2cf33092e2abb60dc0444781c15d0e2e9ecdb37e4b14176a0164027b05900"
        f"e09fa0f61a1882e0b89fbfa5dcfcc9765dd2ca4377e2c794837e091")
    assert response.status_code == 401

    response = client.get(
        f"/auth?password=&password_hash=f34ad4b3ae1e2cf33092e2abb60dc0444781c15d0e2e9ecdb37e4b14176a0164027b05900e09fa"
        f"0f61a1882e0b89fbfa5dcfcc9765dd2ca4377e2c794837e091")
    assert response.status_code == 401

    response = client.get(f"/auth?password=haslo&password_hash=")
    assert response.status_code == 401

    response = client.get(f"/auth?password=&password_hash=")
    assert response.status_code == 401

    response = client.get(f"/auth?")
    assert response.status_code == 401


def test_registration():
    json_file = {"name": "Jan",
                 "surname": "Nowak"}
    response = client.post(
        "/register",
        json=json_file
    )
    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "name": "Jan",
        "surname": "Nowak",
        "register_date": datetime.today().strftime("%Y-%m-%d"),
        "vaccination_date": "2021-04-28",
    }


def test_patient():
    response = client.get("/patient/1")
    assert response.json() == {"id": 1,
                               "name": "Jan",
                               "surname": "Nowak",
                               "register_date": datetime.today().strftime("%Y-%m-%d"),
                               "vaccination_date": (datetime.today() + timedelta(8)).strftime("%Y-%m-%d"),
                               }
    assert response.status_code == 200

    response = client.get("/patient/2")
    assert response.json() == {"id": 2,
                               "name": "Jake",
                               "surname": "Muffin",
                               "register_date": datetime.today().strftime("%Y-%m-%d"),
                               "vaccination_date": (datetime.today() + timedelta(10)).strftime("%Y-%m-%d"),
                               }
    assert response.status_code == 200

    response = client.get("/patient/0")
    assert response.status_code == 400

    response = client.get("/patient/3")
    assert response.status_code == 404



