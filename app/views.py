from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import PositiveInt
from sqlalchemy.orm import Session
from . import crud, schemas, models
from .database import get_db

router = APIRouter()


@router.get("/shippers/{shipper_id}", response_model=schemas.Shipper)
async def get_shipper(shipper_id: PositiveInt, db: Session = Depends(get_db)):
    db_shipper = crud.get_shipper(db, shipper_id)
    if db_shipper is None:
        raise HTTPException(status_code=404, detail="Shipper not found")
    return db_shipper


@router.get("/shippers", response_model=List[schemas.Shipper])
async def get_shippers(db: Session = Depends(get_db)):
    return crud.get_shippers(db)


@router.get("/suppliers", response_model=List[schemas.Suppliers])
async def get_suppliers(db: Session = Depends(get_db)):
    return crud.get_suppliers(db)


@router.get("/suppliers/{supplier_id}", response_model=schemas.Supplier)
async def get_supplier(supplier_id: PositiveInt, db: Session = Depends(get_db)):
    db_supplier = crud.get_supplier(db, supplier_id)
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return db_supplier


@router.get("/suppliers/{supplier_id}/products")
async def get_supplier_products(supplier_id: PositiveInt, db: Session = Depends(get_db)):
    db_supplier_products = crud.get_supplier_products_orm(db, supplier_id)
    if not db_supplier_products:
        raise HTTPException(status_code=404, detail="Supplier's products not found")
    return list(
        [schemas.SupplierProduct(
            ProductID=row.Product.ProductID,
            ProductName=row.Product.ProductName,
            Category=schemas.CategoryData(
                CategoryID=row.Category.CategoryID,
                CategoryName=row.Category.CategoryName
            ),
            Discontinued=row.Product.Discontinued
        ) for row in db_supplier_products]
    )


@router.post("/suppliers", status_code=201, response_model=schemas.ReturnedSupplier)
async def create_supplier(new_supplier: schemas.PostSupplier, db: Session = Depends(get_db)):

    last_supplier = db.query(models.Supplier).order_by(models.Supplier.SupplierID.desc()).first()

    orm_supplier = models.Supplier(**new_supplier.dict())
    orm_supplier.SupplierID = last_supplier.SupplierID + 1

    db.add(orm_supplier)
    db.flush()
    db.commit()

    return orm_supplier
