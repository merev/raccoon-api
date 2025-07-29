from sqlalchemy import Column, String, Text, Integer, JSON, TIMESTAMP, Date, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    address = Column(Text, nullable=False)
    info = Column(Text)
    flat_type = Column(String)
    subscription = Column(String)
    plan = Column(String)
    activities = Column(JSON)
    total_price = Column(Integer)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    service_type = Column(String, nullable=False)
