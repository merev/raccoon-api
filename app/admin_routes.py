from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from sqlalchemy import update, delete
from uuid import UUID
from app import models, schemas, database

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/reservations", response_model=List[schemas.ReservationOut])
async def get_reservations(
    db: AsyncSession = Depends(database.get_db),
    status: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50
):
    query = select(models.Reservation)
    if status:
        query = query.where(models.Reservation.status == status)
    query = query.offset(skip).limit(limit)

    results = await db.execute(query)
    return results.scalars().all()

@router.patch("/reservations/{reservation_id}", response_model=schemas.ReservationOut)
async def update_reservation(
    reservation_id: UUID,
    update_data: schemas.ReservationUpdate,
    db: AsyncSession = Depends(database.get_db)
):
    result = await db.execute(
        select(models.Reservation).where(models.Reservation.id == reservation_id)
    )
    res = result.scalar_one_or_none()
    if not res:
        raise HTTPException(status_code=404, detail="Reservation not found")

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(res, key, value)

    await db.commit()
    await db.refresh(res)
    return res

@router.delete("/reservations/{reservation_id}")
async def delete_reservation(
    reservation_id: UUID,
    db: AsyncSession = Depends(database.get_db)
):
    result = await db.execute(
        select(models.Reservation).where(models.Reservation.id == reservation_id)
    )
    res = result.scalar_one_or_none()
    if not res:
        raise HTTPException(status_code=404, detail="Reservation not found")

    await db.delete(res)
    await db.commit()
    return {"status": "deleted", "reservation_id": str(reservation_id)}
