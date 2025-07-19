from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from schema import CreateMenuItem
from models import MenuItem, Order as OrderModel
from database import SessionLocal
from pydantic import BaseModel
from typing import List


app = FastAPI()




app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




from database import Base, engine
from models import Order

Base.metadata.create_all(bind=engine)
MenuItem.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class CreateOrder(BaseModel):
    item: str

class Order(BaseModel):
    id: int
    item: str
    status: str
    model_config = {
        "from_attributes": True
    }

@app.get("/menu-items")
def get_menu_items(db: Session = Depends(get_db)):
    items = db.query(MenuItem).all()
    return items

@app.get("/orders", response_model=List[Order])
def get_orders(db: Session = Depends(get_db)):
    orders = db.query(OrderModel).all()
    return orders


@app.post("/add-order", response_model=Order)
def add_order(order: CreateOrder, db: Session = Depends(get_db)):
    new_order = OrderModel(item=order.item, status="pending")
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order
    

@app.post("/update-order/{order_id}", response_model=Order)
def update_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
@app.delete("/delete-order/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(order)
    db.commit()
    return {"message": f"Order {order_id} deleted"}
    
@app.post("/add-menu-item")
def add_menu_item(item: CreateMenuItem, db: Session = Depends(get_db)):
    new_item = MenuItem(
        name=item.name,
        price=item.price,
        image=item.image,
        category=item.category
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return {"message": "Menu item added", "item": {
        "id": new_item.id,
        "name": new_item.name,
        "price": new_item.price,
        "image": new_item.image,
        "category": new_item.category
    }}