from pydantic import BaseModel, PositiveInt, constr
from typing import Optional
from typing_extensions import TypedDict


class Shipper(BaseModel):
    ShipperID: PositiveInt
    CompanyName: constr(max_length=40)
    Phone: constr(max_length=24)

    class Config:
        orm_mode = True


class Supplier(BaseModel):
    SupplierID: PositiveInt
    CompanyName: constr(max_length=40)
    ContactName: constr(max_length=30)
    ContactTitle: constr(max_length=30)
    Address: constr(max_length=60)
    City: constr(max_length=15)
    Region: Optional[constr(max_length=15)]
    PostalCode: constr(max_length=10)
    Country: constr(max_length=15)
    Phone: constr(max_length=24)
    Fax: Optional[constr(max_length=24)] = None
    HomePage: Optional[constr(max_length=255)] = None

    class Config:
        orm_mode = True


class Suppliers(BaseModel):
    SupplierID: PositiveInt
    CompanyName: constr(max_length=40)

    class Config:
        orm_mode = True


class Category(BaseModel):
    CategoryID: PositiveInt
    CategoryName: str

    class Config:
        orm_mode = True


class Products(BaseModel):
    ProductID: Optional[PositiveInt]
    ProductName: Optional[constr(max_length=40)]
    Category: Optional[Category]
    Discontinued: Optional[int]

    class Config:
        orm_mode = True
