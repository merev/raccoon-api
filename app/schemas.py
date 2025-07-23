from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date, time, datetime
from uuid import UUID


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

class ReservationOut(BaseModel):
    id: UUID
    name: str
    email: str
    phone: str
    address: str
    info: Optional[str]
    flat_type: str
    subscription: Optional[str]
    plan: Optional[str]
    activities: List[str]
    total_price: int
    date: date
    time: time
    status: str
    created_at: datetime

    class Config:
        orm_mode = True

class ReservationUpdate(BaseModel):
    status: Optional[str]
    notes: Optional[str]  # if you want to store admin notes in future