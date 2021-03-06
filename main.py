import hashlib
from fastapi import FastAPI, Response, Request, Depends, HTTPException, status, Cookie, Query
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.security import HTTPBasicCredentials, HTTPBasic
import secrets
import sqlite3
from app import views


app = FastAPI()
security = HTTPBasic()
app.counter = 0
app.patient_counter = 0
app.patient_list = []
templates = Jinja2Templates(directory="templates")
app.secret_key = "abracadabra"
app.token = []
app.session = []
app.include_router(
    views.router,
    tags=["views"]
)


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


@app.get("/hello")
def hello(request: Request):
    today = datetime.today().strftime("%Y-%m-%d")
    return templates.TemplateResponse(
        "hello.html.j2",
        {"request": request, "date": today}
    )


@app.post("/login_session")
def login_session(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "4dm1n")
    correct_password = secrets.compare_digest(credentials.password, "NotSoSecurePa$$")
    if not(correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    time = datetime.today().strftime("%Y-%m-%d")
    session_token = hashlib.sha256(f"{credentials.username}{credentials.password}"
                                   f"{time}{app.secret_key}".encode()).hexdigest()
    response.set_cookie(key="session_token", value=session_token)
    if len(app.session) >= 3:
        app.session.pop(0)
    app.session.append(session_token)
    response.status_code = 201


@app.post("/login_token", status_code=201)
def login_token(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "4dm1n")
    correct_password = secrets.compare_digest(credentials.password, "NotSoSecurePa$$")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    time = datetime.today().strftime("%Y-%m-%d")
    session_token = hashlib.sha256(f"{credentials.username}{credentials.password}"
                                   f"{time}{app.secret_key}".encode()).hexdigest()
    if len(app.token) >= 3:
        app.token.pop(0)
    app.token.append(session_token)
    return {"token": session_token}


@app.get("/welcome_session")
def welcome_session(format: str = "", session_token: str = Cookie(None)):
    if session_token not in app.session:
        raise HTTPException(status_code=401)
    if format == "json":
        return {"message": "Welcome!"}
    elif format == "html":
        return HTMLResponse(content="<h1>Welcome!</h1>", status_code=200)
    else:
        return PlainTextResponse(content="Welcome!", status_code=200)


@app.get("/welcome_token")
def welcome_token(token: str = "", format: str = ""):
    if (token == "") or (token not in app.token):
        raise HTTPException(status_code=401)
    if format == "json":
        return {"message": "Welcome!"}
    elif format == "html":
        return HTMLResponse(content="<h1>Welcome!</h1>", status_code=200)
    else:
        return PlainTextResponse(content="Welcome!", status_code=200)


@app.delete("/logout_session")
def logout_session(format: str = "", session_token: str = Cookie(None)):
    if session_token not in app.session:
        raise HTTPException(status_code=401)

    app.session.remove(session_token)
    url = "/logged_out?format=" + format
    return RedirectResponse(url=url, status_code=303)


@app.delete("/logout_token")
def logout_token(token: str = "", format: str = ""):
    if (token == "") or (token not in app.token):
        raise HTTPException(status_code=401)

    app.token.remove(token)
    url = "/logged_out?format=" + format
    return RedirectResponse(url=url, status_code=303)


@app.get("/logged_out", status_code=200)
def logged_out(format: str = ""):
    if format == "json":
        return {"message": "Logged out!"}
    elif format == "html":
        return HTMLResponse(content="<h1>Logged out!</h1>", status_code=200)
    else:
        return PlainTextResponse(content="Logged out!", status_code=200)


"""DATABASE"""


@app.on_event('startup')
async def startup():
    app.db_connection = sqlite3.connect('northwind.db')
    app.db_connection.text_factory = lambda b: b.decode(errors='ignore')


@app.on_event('shutdown')
async def shutdown():
    app.db_connection.close()


@app.get('/categories')
async def categories():
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute(
        'SELECT CategoryID, CategoryName FROM Categories'
    ).fetchall()
    return {
        'categories': [{'id': x['CategoryID'], 'name': x['CategoryName']} for x in data]
    }


@app.get('/customers')
async def customers():
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute(
        'SELECT CustomerID, CompanyName,'
        'Address || " " || PostalCode || " " || City || " " || Country AS FullAddress FROM Customers'
    ).fetchall()
    return {
        'customers': [{'id': x['CustomerID'],
                       'name': x['CompanyName'],
                       'full_address': x['FullAddress']} for x in data]
    }


@app.get("/products/{id}")
async def product(id: int):
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute(
        "SELECT ProductID, ProductName FROM Products WHERE ProductID = :id",
        {'id': id}).fetchone()
    if data is None:
        raise HTTPException(status_code=404)
    else:
        return {
            'id': id,
            'name': data['ProductName']
        }


def view_order(order):
    if order not in {"first_name", "last_name", "city", "EmployeeID"}:
        raise HTTPException(status_code=400)


@app.get("/employees")
async def employees(limit: Optional[int] = Query(None), offset: Optional[int] = Query(None),
                    order: Optional[str] = Query('EmployeeID')):
    view_order(order)
    order = ''.join([word.capitalize() for word in order.split("_")])
    app.db_connection.row_factory = sqlite3.Row
    query = f"SELECT EmployeeID, LastName, FirstName, City FROM Employees ORDER BY {order} ASC"
    if limit is not None:
        query += f" LIMIT {limit}"
    if offset is not None:
        query += f" OFFSET {offset}"
    data = app.db_connection.execute(query).fetchall()
    return {
        "employees": [
            {
                "id": x["EmployeeID"],
                "last_name": x["LastName"],
                "first_name": x["FirstName"],
                "city": x["City"],
            }
            for x in data
        ]
    }


@app.get('/products_extended')
async def products_extended():
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute(
        'SELECT ProductID, ProductName, CategoryName, CompanyName FROM Products JOIN Categories'
        ' ON Products.CategoryID = Categories.CategoryID JOIN Suppliers ON Products.SupplierID = Suppliers.SupplierID'
    )
    return {
        'products_extended': [
            {
                'id': x['ProductID'],
                'name': x['ProductName'],
                'category': x['CategoryName'],
                'supplier': x['CompanyName'],
            }
            for x in data
        ]
    }


def check_product(id: int):
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute(
        "SELECT ProductID FROM Products WHERE ProductID = :product_id",
        {"product_id": id},
    ).fetchone()
    return False if data is None else True


@app.get("/products/{id}/orders")
async def orders(id: int):
    if not check_product(id):
        raise HTTPException(status_code=404)
    data = app.db_connection.execute(
        "SELECT Products.ProductID, Orders.OrderID, Customers.CompanyName, 'Order Details'.Quantity, "
        "ROUND(('Order Details'.UnitPrice * 'Order Details'.Quantity) - ('Order Details'.Discount * "
        "('Order Details'.UnitPrice * 'Order Details'.Quantity)), 2) AS TotalPrice FROM Products JOIN 'Order Details'"
        " ON Products.ProductID = 'Order Details'.ProductID JOIN Orders ON 'Order Details'.OrderID = Orders.OrderID "
        "JOIN Customers ON Orders.CustomerID = Customers.CustomerID WHERE Products.ProductID = :product_id",
        {"product_id": id},
    ).fetchall()
    return {
        "orders": [
            {
                "id": x["OrderID"],
                "customer": x["CompanyName"],
                "quantity": x["Quantity"],
                "total_price": x["TotalPrice"],
            }
            for x in data
        ]
    }


class Category(BaseModel):
    name: str


@app.post('/categories', status_code=status.HTTP_201_CREATED)
async def new_category(category: Category):
    cursor = app.db_connection.execute(
        f"INSERT INTO Categories (CategoryName) VALUES ('{category.name}')"
    )
    app.db_connection.commit()
    new_category_id = cursor.lastrowid
    app.db_connection.row_factory = sqlite3.Row
    return {
        "id": new_category_id,
        "name": category.name
    }


def check_category(id: int):
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute(
        "SELECT CategoryID FROM Categories WHERE CategoryID = :category_id",
        {"category_id": id},
    ).fetchone()
    return False if data is None else True


@app.put("/categories/{id}")
async def add_category(id: int, category: Category):
    if not check_category(id):
        raise HTTPException(status_code=404)
    cursor = app.db_connection.execute(
        "UPDATE Categories SET CategoryName = :category_name WHERE CategoryID = :category_id",
        {"category_name": category.name, "category_id": id},
    )
    app.db_connection.commit()
    data = app.db_connection.execute(
        "SELECT CategoryID, CategoryName FROM Categories WHERE CategoryID = :category_id",
        {"category_id": id},
    ).fetchone()
    return {"id": data["CategoryID"], "name": data["CategoryName"]}


@app.delete("/categories/{id}")
async def delete_category(id: int):
    if not check_category(id):
        raise HTTPException(status_code=404)
    cursor = app.db_connection.execute(
        "DELETE FROM Categories WHERE CategoryID = :category_id", {"category_id": id}
    )
    app.db_connection.commit()
    return {"deleted": cursor.rowcount}
