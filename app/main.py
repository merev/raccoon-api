from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import models, schemas, database
from sqlalchemy.exc import SQLAlchemyError
from app.mail_utils import send_reservation_email, verify_decline_token
from sqlalchemy import update
import asyncio
from app.contact import router as contact_router
from app.telegram import send_telegram_message
from app.admin_routes import router as admin_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(root_path="/api")

app.include_router(contact_router)
app.include_router(admin_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://admin-staging.raccoon.bg"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
            date=reservation.date,
            time=reservation.time,
            service_type=reservation.service_type
        )
        db.add(new_res)
        await db.commit()
        await db.refresh(new_res)

        await send_telegram_message(
            f"📩 *Нова резервация!* - {new_res.service_type}\n\n"
            f"👤 *Име:* {new_res.name}\n"
            f"📞 *Тел:* {new_res.phone}\n"
            f"🏠 *Адрес:* {new_res.address}\n"
            f"🏢 *Тип:* {new_res.flat_type}\n"
            f"📦 *План:* {new_res.plan or 'Потребителски'}\n"
            f"🧹 *Дейности:* {', '.join(new_res.activities)}\n"
            f"💰 *Цена:* {new_res.total_price} лв\n"
            f"📅 *Дата:* {new_res.date}\n"
            f"🕒 *Час:* {new_res.time.strftime('%H:%M')}"
        )

        send_reservation_email(
            to_email=reservation.email,
            reservation_data={
                "reservation_id": str(new_res.id),
                "flat_type": reservation.flat_type,
                "plan": reservation.plan or "Потребителски",
                "total_price": reservation.total_price,
                "date": str(reservation.date),
                "time": str(reservation.time)[:5]
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