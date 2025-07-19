
from pydantic import BaseModel

class CreateMenuItem(BaseModel):
    name: str
    price: float
    image: str = ""
    category: str = ""