from fastapi.testclient import TestClient
from main import app
import pytest

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