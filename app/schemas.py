from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date, time

class ReservationIn(BaseModel):
    name: str
    email: EmailStr
    phone: str
    address: str
    info: Optional[str]
    flat_type: str
    subscription: str
    plan: Optional[str]
    activities: Optional[List[str]]
    total_price: int
    date: date
    time: time
