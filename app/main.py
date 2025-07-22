from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import models, schemas, database
from sqlalchemy.exc import SQLAlchemyError
import asyncio

app = FastAPI(root_path="/api")

@app.on_event("startup")
async def startup():
    for i in range(10):
        try:
            async with database.engine.begin() as conn:
                await conn.run_sync(models.Base.metadata.create_all)
            break
        except Exception as e:
            print(f"DB not ready yet, retrying... ({i + 1}/10)")
            await asyncio.sleep(2)

@app.post("/reservations")
async def create_reservation(reservation: schemas.ReservationIn, db: AsyncSession = Depends(database.get_db)):
    try:
        new_res = models.Reservation(
            name=reservation.name,
            email=reservation.email,
            phone=reservation.phone,
            address=reservation.address,
            info=reservation.info,
            flat_type=reservation.flat_type,
            subscription=reservation.subscription,
            plan=reservation.plan,
            activities=reservation.activities,
            total_price=reservation.total_price,
        )
        db.add(new_res)
        await db.commit()
        await db.refresh(new_res)
        return {"status": "success", "reservation_id": str(new_res.id)}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
