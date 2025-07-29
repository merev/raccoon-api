from pydantic import BaseModel, EmailStr, model_validator
from typing import List, Optional, Literal, Generic, TypeVar
from datetime import date, time, datetime
from uuid import UUID


T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    total: int
    page: int
    per_page: int

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
    service_type: str

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
    service_type: str

    class Config:
        from_attributes = True

class ReservationUpdate(BaseModel):
    status: Optional[Literal["pending", "confirmed", "declined", "completed"]] = None
    notes: Optional[str] = None # if you want to store admin notes in future

    @model_validator(mode='before')
    def validate_update(cls, values):
        if not values:
            raise ValueError("Request body cannot be empty")
        return values


class ReservationFilter(BaseModel):
    name: Optional[str]
    status: Optional[str]
    subscription: Optional[str]
    service_type: str
    date_from: Optional[date]
    date_to: Optional[date]
    page: int = 1
    limit: int = 10
