from typing import Optional
from datetime import datetime, timezone
from backend.db.session import transactional_session
from backend.models.part_orders import PartOrder
from backend.models.order_items import OrderItem
from backend.models.order_parts_status import OrderPartsStatus
from sqlalchemy.orm import Session
from backend.validations.output_validators import validate_part_order


class PartsOrderService:
    @staticmethod
    def create_order(skladajacy_id: int, db: Optional[Session] = None) -> PartOrder:
        if db is not None:
            status = (
                db.query(OrderPartsStatus)
                .filter(OrderPartsStatus.nazwa_statusu == "oczekujace na zatwierdzenie")
                .first()
            )
            if not status:
                raise ValueError(
                    "Brak statusu 'oczekujace na zatwierdzenie' w bazie danych."
                )

            order = PartOrder(
                id_skladajacego=skladajacy_id,
                status_zamowienia=status.id_statusu,
                data_zlozenia=datetime.now(timezone.utc),
            )

            db.add(order)
            db.flush()
            db.refresh(order)
            validate_part_order(order)
            return order

        with transactional_session() as db_sess:
            status = (
                db_sess.query(OrderPartsStatus)
                .filter(OrderPartsStatus.nazwa_statusu == "oczekujace na zatwierdzenie")
                .first()
            )
            if not status:
                raise ValueError(
                    "Brak statusu 'oczekujace na zatwierdzenie' w bazie danych."
                )

            order = PartOrder(
                id_skladajacego=skladajacy_id,
                status_zamowienia=status.id_statusu,
                data_zlozenia=datetime.now(timezone.utc),
            )

            db_sess.add(order)
            db_sess.flush()
            db_sess.refresh(order)
            validate_part_order(order)
            return order

    @staticmethod
    def add_item(
        order_id: int, part_id: int, ilosc: int, cena_jednostkowa: float, db: Optional[Session] = None
    ) -> OrderItem:
        if db is not None:
            order = db.query(PartOrder).filter(PartOrder.id_zamowienia == order_id).first()

            if not order:
                raise ValueError(f"Nie znaleziono zamowienia o id={order_id}")

            item = OrderItem(
                id_zamowienia=order_id,
                id_czesci=part_id,
                ilosc=ilosc,
                cena_jednostkowa=cena_jednostkowa,
            )

            db.add(item)
            db.flush()
            db.refresh(item)
            return item

        with transactional_session() as db_sess:
            order = db_sess.query(PartOrder).filter(PartOrder.id_zamowienia == order_id).first()

            if not order:
                raise ValueError(f"Nie znaleziono zamowienia o id={order_id}")

            item = OrderItem(
                id_zamowienia=order_id,
                id_czesci=part_id,
                ilosc=ilosc,
                cena_jednostkowa=cena_jednostkowa,
            )

            db_sess.add(item)
            db_sess.flush()
            db_sess.refresh(item)
            return item

    @staticmethod
    def change_status(
        order_id: int, status_name: str, zatwierdzajacy_id: int | None = None, db: Optional[Session] = None
    ) -> PartOrder:
        if db is not None:
            order = db.query(PartOrder).filter(PartOrder.id_zamowienia == order_id).first()
            if not order:
                raise ValueError(f"Nie znaleziono zamowienia o id={order_id}")

            status = (
                db.query(OrderPartsStatus)
                .filter(OrderPartsStatus.nazwa_statusu == status_name)
                .first()
            )
            if not status:
                raise ValueError(f"Nie znaleziono statusu o nazwie '{status_name}'")

            order.status_zamowienia = status.id_statusu
            if zatwierdzajacy_id is not None:
                order.id_zatwierdzajacego = zatwierdzajacy_id

            lower = status_name.lower()
            if lower == "zatwierdzone":
                order.data_zatwierdzenia = datetime.now(timezone.utc)
            elif lower == "odebrane":
                order.data_realizacji = datetime.now(timezone.utc)

            db.flush()
            db.refresh(order)
            return order

        with transactional_session() as db_sess:
            order = db_sess.query(PartOrder).filter(PartOrder.id_zamowienia == order_id).first()
            if not order:
                raise ValueError(f"Nie znaleziono zamowienia o id={order_id}")

            status = (
                db_sess.query(OrderPartsStatus)
                .filter(OrderPartsStatus.nazwa_statusu == status_name)
                .first()
            )
            if not status:
                raise ValueError(f"Nie znaleziono statusu o nazwie '{status_name}'")

            order.status_zamowienia = status.id_statusu
            if zatwierdzajacy_id is not None:
                order.id_zatwierdzajacego = zatwierdzajacy_id

            lower = status_name.lower()
            if lower == "zatwierdzone":
                order.data_zatwierdzenia = datetime.now(timezone.utc)
            elif lower == "odebrane":
                order.data_realizacji = datetime.now(timezone.utc)

            db_sess.flush()
            db_sess.refresh(order)
            return order

    @staticmethod
    def list_orders(db: Optional[Session] = None) -> list[PartOrder]:
        if db is not None:
            return db.query(PartOrder).all()
        with transactional_session() as db_sess:
            return db_sess.query(PartOrder).all()
