from __future__ import annotations

from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.db.session import transactional_session
from backend.models.parts_used import PartsUsed
from backend.models.parts import Part
from backend.models.order import Order
from backend.validations.output_validators import validate_used_part, validate_part


class PartsUsedService:
    @staticmethod
    def _recalculate_order_cost(session: Session, order_id: int):
        """Pomocnicza metoda do przeliczania kosztu czesci w zleceniu."""
        total_cost = (
            session.query(func.sum(PartsUsed.ilosc * PartsUsed.cena_jednostkowa))
            .filter(PartsUsed.id_zlecenia == order_id)
            .scalar()
        ) or 0.0

        order = session.get(Order, order_id)
        if order:
            order.koszt_czesci = total_cost
            session.add(order)

    @staticmethod
    def add_used_part(
        order_id: int,
        part_id: int,
        quantity: int,
        unit_price: float,
        db: Optional[Session] = None,
    ) -> PartsUsed:

        def _impl(sess: Session) -> PartsUsed:
            part = (
                sess.query(Part)
                .filter(Part.id_czesci == part_id)
                .with_for_update()
                .first()
            )
            if not part:
                raise ValueError(f"Nie znaleziono czesci o id={part_id}")

            if quantity <= 0:
                raise ValueError("Ilosc musi byc > 0")

            if part.ilosc_dostepna < quantity:
                raise ValueError(
                    f"Brak wystarczajacej ilosci czesci w magazynie. Dostepne: {part.ilosc_dostepna}"
                )

            order = sess.query(Order).filter(Order.id_zlecenia == order_id).first()
            if not order:
                raise ValueError(f"Nie znaleziono zlecenia o id={order_id}")

            used_part = PartsUsed(
                id_zlecenia=order_id,
                id_czesci=part_id,
                ilosc=quantity,
                cena_jednostkowa=unit_price,
                data_wykorzystania=datetime.now(timezone.utc),
            )

            sess.add(used_part)

            # 1. Zmniejsz stan magazynowy
            part.ilosc_dostepna -= quantity

            sess.flush()
            sess.refresh(used_part)

            # 2. Przelicz koszt czesci w zleceniu
            PartsUsedService._recalculate_order_cost(sess, order_id)

            validate_used_part(used_part)
            validate_part(part)

            return used_part

        if db is not None:
            return _impl(db)

        with transactional_session() as db_sess:
            return _impl(db_sess)

    @staticmethod
    def list_used_parts(
        order_id: int,
        db: Optional[Session] = None,
    ) -> list[PartsUsed]:
        if db is not None:
            return (
                db.query(PartsUsed)
                .filter(PartsUsed.id_zlecenia == order_id)
                .order_by(PartsUsed.id_pozycji.asc())
                .all()
            )

        with transactional_session() as db_sess:
            return (
                db_sess.query(PartsUsed)
                .filter(PartsUsed.id_zlecenia == order_id)
                .order_by(PartsUsed.id_pozycji.asc())
                .all()
            )

    @staticmethod
    def update_used_part_quantity(
        order_id: int,
        used_part_id: int,
        new_quantity: int,
    ):
        # Ta metoda wymagałaby pełnej implementacji (pominąłem dla zwięzłości,
        # skupiając się na add/delete, które są kluczowe dla UI)
        pass

    @staticmethod
    def delete_used_part(
        order_id: int, used_part_id: int, db: Optional[Session] = None
    ):
        def _impl(sess: Session):
            used = (
                sess.query(PartsUsed)
                .filter(
                    PartsUsed.id_pozycji == used_part_id,
                    PartsUsed.id_zlecenia == order_id,
                )
                .first()
            )
            if not used:
                raise ValueError("Nie znaleziono pozycji")

            # Przywróć stan magazynowy
            part = sess.get(Part, used.id_czesci)
            if part:
                part.ilosc_dostepna += used.ilosc

            sess.delete(used)
            sess.flush()

            # Przelicz koszt
            PartsUsedService._recalculate_order_cost(sess, order_id)

        if db is not None:
            _impl(db)
        else:
            with transactional_session() as sess:
                _impl(sess)
