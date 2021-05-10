import sqlite3

from fastapi import Cookie, FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel


app = FastAPI()


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
