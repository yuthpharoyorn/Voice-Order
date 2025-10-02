from sqlalchemy import Column, Integer, String, Float
from database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    item = Column(String(255), nullable=False)
    status = Column(String(50), default="pending")
    price = Column(Float, default=0.0)
    
    

class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, default=0.0)
    category = Column(String(50), nullable=True)
    image = Column(String(255), nullable=True)
    
class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="admin")


