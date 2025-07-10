from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

orders = []

class CreateOrder(BaseModel):
    item: str

class Order(BaseModel):
    id: int
    item: str
    status: str

@app.get("/orders", response_model=List[Order])
def get_orders():
    return orders

@app.post("/add-order", resonse_model=Order)
def add_order(order: CreateOrder):
    new_order = {
        "id": len(orders) +1,
        "item": order.item,
        "status": "pending"
    }

    orders.append(new_order)
    return new_order

@app.post("/update-order/{order_id}", respone_model= Order)
def update_order(order_id: int):
    for order in orders:
        if order['id']== order_id:
            order['status']= "done"
            return order
        raise HTTPException(status_code=404, detail="Order not found")
    
@app.delete("/delete-order/{order_id}")
def delete_order(order_id: int):
    global orders 
    for order in orders:
        if order['id']== order_id:
            orders = [o for o in orders if o['id']!=order_id]
            return {"message": f"Order {order_id} deleted"}
    raise HTTPException(status_code=404, detail="Order not found")
