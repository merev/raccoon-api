from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from uuid import UUID
from typing import List, Optional
from datetime import date

from app import models, schemas, database

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/reservations", response_model=List[schemas.ReservationOut])
async def get_reservations(
    db: AsyncSession = Depends(database.get_db),
    name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100)
):
    query = select(models.Reservation)
    filters = []

    if name:
        filters.append(models.Reservation.name.ilike(f"%{name}%"))
    if status:
        filters.append(models.Reservation.status == status)
    if date_from:
        filters.append(models.Reservation.date >= date_from)
    if date_to:
        filters.append(models.Reservation.date <= date_to)

    if filters:
        query = query.where(and_(*filters))

    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)

    results = await db.execute(query)
    return results.scalars().all()


@router.patch("/reservations/{reservation_id}", response_model=schemas.ReservationOut)
async def update_reservation(
    reservation_id: UUID,
    update_data: schemas.ReservationUpdate,
    db: AsyncSession = Depends(database.get_db)
):
    # Validate UUID exists
    try:
        reservation_id = UUID(str(reservation_id))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid reservation ID format"
        )

    # Get reservation
    res = await db.scalar(
        select(models.Reservation).where(models.Reservation.id == reservation_id)
    )
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )

    # Apply updates
    update_values = update_data.model_dump(exclude_unset=True)
    for field, value in update_values.items():
        setattr(res, field, value)

    try:
        await db.commit()
        await db.refresh(res)
        return res
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


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
