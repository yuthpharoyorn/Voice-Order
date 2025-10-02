from datetime import date,datetime,timedelta
from fastapi import FastAPI, HTTPException, Depends,status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from schema import CreateMenuItem
from models import Admin, MenuItem, Order as OrderModel 
from database import SessionLocal
from pydantic import BaseModel
from typing import List
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer





ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

load_dotenv(dotenv_path="unknown.txt")

SECRET_KEY = os.getenv("SECRET_KEY")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)

def get_admin_by_username(db: Session, username: str):
    return db.query(Admin).filter(Admin.username == username).first()

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://192.168.86.1:3000",  # <-- add this
    ],
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
    image: str 

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
    item.image = data.image
    db.commit()
    db.refresh(item)

    return {
        "message": "Menu item updated successfully",
        "item": {
            "id": item.id,
            "price": item.price,
            "category": item.category,
            "image": item.image

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

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_admin_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")
        if username is None or role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized")
        return {"username": username, "role": role}
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

@app.get("/admin/dashboard")
def admin_dashboard(current_user: dict = Depends(get_current_user)):
    return {"message": f"Welcome {current_user['username']} to the admin dashboard!"}

@app.post("/create-admin")
def create_admin(username: str, password: str, db: Session = Depends(get_db)):
    existing = db.query(Admin).filter(Admin.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    admin = Admin(username=username, hashed_password=hash_password(password))
    db.add(admin)
    db.commit()
    return {"message": f"Admin '{username}' created successfully"}