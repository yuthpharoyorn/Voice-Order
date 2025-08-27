from datetime import date
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from schema import CreateMenuItem
from models import MenuItem, Order as OrderModel 
from database import SessionLocal
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from database import Base, engine

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class CreateOrder(BaseModel):
    item: str
    price: float =0.0
   

class OrderResponse(BaseModel): 
    id: int
    item: str
    status: str
    price: float = 0.0

    model_config = {
        "from_attributes": True
    }

class ItemUpdate(BaseModel):
    id: int
    price: float
    category: str

@app.get("/menu-items")
def get_menu_items(db: Session = Depends(get_db)):
    items = db.query(MenuItem).all()
    return items

@app.get("/orders", response_model=List[OrderResponse])  
def get_orders(db: Session = Depends(get_db)):
    orders = db.query(OrderModel).all()
    return orders

@app.post("/add-order", response_model=OrderResponse) 
def add_order(order: CreateOrder, db: Session = Depends(get_db)):
    new_order = OrderModel(item=order.item, status="pending", price=order.price) 
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

@app.put("/update-order/{order_id}", response_model=OrderResponse)  # Use OrderResponse
def update_order(order_id: int, update_data: dict, db: Session = Depends(get_db)):
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
  
    if "status" in update_data:
        order.status = update_data["status"]
          
    db.commit()
    db.refresh(order)
    return order

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

@app.post("/checkout")
def checkout(data: dict, db: Session = Depends(get_db)):
    items = data.get("items", [])
    for item in items:
        new_order = OrderModel(item=item["name"], status="pending", price=item.get("price", 0.0))  # ✅ Just add price
        db.add(new_order)
    db.commit()
    return {"message": "Order(s) placed"}

# FIXED: Get admin statistics
@app.get("/admin/stats")
def get_admin_stats(db: Session = Depends(get_db)):
    try:
        # Count total orders using OrderModel (not Order)
        total_orders = db.query(OrderModel).count()
        
        # Count active orders (pending/preparing status)
        active_orders = db.query(OrderModel).filter(
            OrderModel.status.in_(['pending', 'preparing'])
        ).count()
        total_revenue = db.query(func.sum(OrderModel.price)).scalar() or 0.0
        completed_revenue = db.query(func.sum(OrderModel.price)).filter(
            OrderModel.status == "completed"
        ).scalar() or 0.0
        
        # For now, return simple stats since we don't have date/revenue fields yet
        return {
            "total_orders": total_orders,
            "today_orders": total_orders,  # Simplified for now
            "active_orders": active_orders,
            "today_revenue": completed_revenue,
            "total_revenue": total_revenue
        }
        
    except Exception as e:
        print(f"Error in get_admin_stats: {e}") 
        raise HTTPException(status_code=500, detail=str(e))
    

        


@app.get("/admin/orders")
def get_all_orders(db: Session = Depends(get_db)):
    try:
        orders = db.query(OrderModel).all()  # 
        return {"orders": orders}
    except Exception as e:
        print(f"Error in get_all_orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/revenue")
def get_revenue(db: Session = Depends(get_db)):
    try:
        revenue = db.query(func.sum(OrderModel.price)).filter(OrderModel.status == "completed").scalar()
        return {"revenue": revenue}
    except Exception as e:
        print(f"Error in get_revenue: {e}")  # Debug print
        raise HTTPException(status_code=500, detail=str(e))
    

@app.put("/menu/items")
def update_menu_item(data: ItemUpdate, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(MenuItem.id == data.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    item.price = data.price
    item.category = data.category
    db.commit()
    db.refresh(item)

    return {
        "message": "Menu item updated successfully",
        "item": {
            "id": item.id,
            "price": item.price,
            "category": item.category
        }
    }

@app.delete("/menu/items/{item_id}")
def delete_menu_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    db.delete(item)
    db.commit()
    return {"message": "Menu item deleted successfully"}

@app.post("/menu/items")
def create_menu_item(item: CreateMenuItem, db: Session = Depends(get_db)):
    new_item = MenuItem(
        name=item.name,
        price=item.price,
        image=item.image,
        category=item.category
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return {"message": "Menu item created successfully", "item": {
        "id": new_item.id,
        "name": new_item.name,
        "price": new_item.price,
        "image": new_item.image,
        "category": new_item.category
    }}
