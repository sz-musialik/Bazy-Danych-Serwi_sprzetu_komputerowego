from typing import Optional
from backend.models.parts_used import PartsUsed
from backend.models.parts import Part
from backend.models.order import Order
from backend.db.session import transactional_session
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from backend.validations.output_validators import validate_used_part, validate_part


class PartsUsedService:
    @staticmethod
    def add_used_part(order_id: int, part_id: int, quantity: int, unit_price: float, db: Optional[Session] = None) -> PartsUsed:
        if db is not None:
            part = db.query(Part).filter(Part.id_czesci == part_id).with_for_update().first()
            if not part:
                raise ValueError(f"Nie znaleziono czesci o id={part_id}")

            if part.ilosc_dostepna < quantity:
                raise ValueError(
                    f"Brak wystarczajacej ilosci czesci w magazynie. Dostepne: {part.ilosc_dostepna}"
                )

            order = db.query(Order).filter(Order.id_zlecenia == order_id).first()
            if not order:
                raise ValueError(f"Nie znaleziono zlecenia o id={order_id}")

            used_part = PartsUsed(
                id_zlecenia=order_id,
                id_czesci=part_id,
                ilosc=quantity,
                cena_jednostkowa=unit_price,
                data_wykorzystania=datetime.now(timezone.utc),
            )

            db.add(used_part)
            part.ilosc_dostepna -= quantity
            db.flush()
            db.refresh(used_part)
            validate_used_part(used_part)
            validate_part(part)
            return used_part

        with transactional_session() as db_sess:
            part = db_sess.query(Part).filter(Part.id_czesci == part_id).with_for_update().first()
            if not part:
                raise ValueError(f"Nie znaleziono czesci o id={part_id}")

            if part.ilosc_dostepna < quantity:
                raise ValueError(
                    f"Brak wystarczajacej ilosci czesci w magazynie. Dostepne: {part.ilosc_dostepna}"
                )

            order = db_sess.query(Order).filter(Order.id_zlecenia == order_id).first()
            if not order:
                raise ValueError(f"Nie znaleziono zlecenia o id={order_id}")

            used_part = PartsUsed(
                id_zlecenia=order_id,
                id_czesci=part_id,
                ilosc=quantity,
                cena_jednostkowa=unit_price,
                data_wykorzystania=datetime.now(timezone.utc),
            )

            db_sess.add(used_part)

            part.ilosc_dostepna -= quantity

            db_sess.flush()
            db_sess.refresh(used_part)
            validate_used_part(used_part)
            validate_part(part)
            return used_part

    @staticmethod
    def list_used_parts(order_id: int, db: Optional[Session] = None) -> list[PartsUsed]:
        if db is not None:
            return db.query(PartsUsed).filter(PartsUsed.id_zlecenia == order_id).all()
        with transactional_session() as db_sess:
            return db_sess.query(PartsUsed).filter(PartsUsed.id_zlecenia == order_id).all()
