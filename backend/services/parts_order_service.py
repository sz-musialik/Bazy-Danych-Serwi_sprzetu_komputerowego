from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from backend.db.session import transactional_session
from backend.models.part_orders import PartOrder
from backend.models.order_items import OrderItem
from backend.models.order_parts_status import OrderPartsStatus
from backend.validations.output_validators import validate_part_order


class PartsOrderService:

    @staticmethod
    def create_order(skladajacy_id: int, db: Optional[Session] = None) -> int:

        def _create(session: Session) -> int:
            status = (
                session.query(OrderPartsStatus)
                .filter(OrderPartsStatus.nazwa_statusu == "oczekujace na zatwierdzenie")
                .first()
            )
            if not status:
                raise ValueError("Brak statusu 'oczekujace na zatwierdzenie'")

            order = PartOrder(
                id_skladajacego=skladajacy_id,
                status_zamowienia=status.id_statusu,
                data_zlozenia=datetime.now(timezone.utc),
            )

            session.add(order)
            session.flush()
            validate_part_order(order)
            return order.id_zamowienia

        if db is not None:
            return _create(db)

        with transactional_session() as session:
            return _create(session)

    @staticmethod
    def add_item(
        order_id: int,
        part_id: int,
        ilosc: int,
        cena_jednostkowa: float,
        db: Optional[Session] = None,
    ) -> int:

        def _add(session: Session) -> int:
            order = session.get(PartOrder, order_id)
            if not order:
                raise ValueError(f"Nie znaleziono zamowienia o id={order_id}")

            item = OrderItem(
                id_zamowienia=order_id,
                id_czesci=part_id,
                ilosc=ilosc,
                cena_jednostkowa=cena_jednostkowa,
            )

            session.add(item)
            session.flush()
            return item.id_pozycji

        if db is not None:
            return _add(db)

        with transactional_session() as session:
            return _add(session)

    @staticmethod
    def change_status(
        order_id: int,
        status_name: str,
        zatwierdzajacy_id: int | None = None,
        db: Optional[Session] = None,
    ) -> dict:

        def _change(session: Session) -> dict:
            order = session.get(PartOrder, order_id)
            if not order:
                raise ValueError("Zamówienie nie istnieje")

            status = (
                session.query(OrderPartsStatus)
                .filter(OrderPartsStatus.nazwa_statusu == status_name)
                .first()
            )
            if not status:
                raise ValueError(f"Nie znaleziono statusu '{status_name}'")

            order.status_zamowienia = status.id_statusu
            order.id_zatwierdzajacego = zatwierdzajacy_id

            if status_name.lower() == "zatwierdzone":
                order.data_zatwierdzenia = datetime.now(timezone.utc)
            elif status_name.lower() == "zrealizowane":
                order.data_realizacji = datetime.now(timezone.utc)

            session.flush()

            return {
                "id_zamowienia": order.id_zamowienia,
                "status_zamowienia": status.nazwa_statusu,
            }

        if db is not None:
            return _change(db)

        with transactional_session() as session:
            return _change(session)

    @staticmethod
    def list_orders(db: Optional[Session] = None) -> list[dict]:

        def serialize(o: PartOrder) -> dict:
            return {
                "id_zamowienia": o.id_zamowienia,
                "id_skladajacego": o.id_skladajacego,
                "status_zamowienia": o.status_zamowienia,
                "data_zlozenia": o.data_zlozenia.isoformat() if o.data_zlozenia else None,
            }

        def _list(session: Session):
            return [serialize(o) for o in session.query(PartOrder).all()]

        if db is not None:
            return _list(db)

        with transactional_session() as session:
            return _list(session)
