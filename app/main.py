from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import models, schemas, database
from sqlalchemy.exc import SQLAlchemyError
from app.mail_utils import send_reservation_email, verify_decline_token
from sqlalchemy import update
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

        send_reservation_email(
            to_email=reservation.email,
            reservation_data={
                "reservation_id": str(new_res.id),
                "flat_type": reservation.flat_type,
                "plan": reservation.plan or "Потребителски",
                "total_price": reservation.total_price
            }
        )

        return {"status": "success", "reservation_id": str(new_res.id)}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reservations/decline")
async def decline_reservation(token: str, db: AsyncSession = Depends(database.get_db)):
    try:
        reservation_id = verify_decline_token(token)
        stmt = update(models.Reservation).where(models.Reservation.id == reservation_id).values(status="declined")
        await db.execute(stmt)
        await db.commit()
        return {"status": "declined", "reservation_id": reservation_id}
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")