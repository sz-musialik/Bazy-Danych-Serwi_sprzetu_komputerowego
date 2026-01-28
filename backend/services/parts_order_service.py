from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from backend.db.session import transactional_session
from backend.models.part_orders import PartOrder
from backend.models.order_items import OrderItem
from backend.models.order_parts_status import OrderPartsStatus
from backend.validations.output_validators import validate_part_order
from backend.models.parts import Part
from backend.models.user import User


class PartsOrderService:

    @staticmethod
    def submit_order(order_data: dict, db: Optional[Session] = None) -> int:
        def _submit(session: Session) -> int:
            user_id = order_data.get("id_skladajacego")
            if not user_id:
                raise ValueError("Brak ID składającego zamówienie")

            user = session.get(User, user_id)
            if not user:
                raise ValueError(f"Nie znaleziono użytkownika o ID={user_id}")

            user_role = user.role.nazwa_rola.lower() if user.role else ""

            # Logika statusow
            if user_role in ["administrator", "manager"]:
                target_status = "Zatwierdzone"
                approved_by = user_id
                approved_date = datetime.now(timezone.utc)
            else:
                target_status = "Do zatwierdzenia"
                approved_by = None
                approved_date = None

            status_obj = (
                session.query(OrderPartsStatus)
                .filter(OrderPartsStatus.nazwa_statusu == target_status)
                .first()
            )
            if not status_obj:
                raise ValueError(f"Brak statusu '{target_status}' w bazie danych")

            # Obsluga czesci
            part_name = order_data.get("nazwa_czesci")
            part = session.query(Part).filter(Part.nazwa_czesci == part_name).first()

            if not part:
                part = Part(
                    nazwa_czesci=part_name,
                    typ_czesci=order_data.get("typ_czesci"),
                    producent=order_data.get("producent"),
                    numer_katalogowy=order_data.get("numer_katalogowy"),
                    cena_katalogowa=order_data.get("cena_katalogowa"),
                    ilosc_dostepna=0,
                )
                session.add(part)
                session.flush()

            order = PartOrder(
                id_skladajacego=user_id,
                id_zatwierdzajacego=approved_by,
                status_zamowienia=status_obj.id_statusu,
                data_zlozenia=datetime.now(timezone.utc),
                data_zatwierdzenia=approved_date,
            )
            session.add(order)
            session.flush()

            price = order_data.get("cena_katalogowa")
            qty = order_data.get("ilosc", 1)

            item = OrderItem(
                id_zamowienia=order.id_zamowienia,
                id_czesci=part.id_czesci,
                ilosc=qty,
                cena_jednostkowa=price,
            )
            session.add(item)
            session.flush()

            return order.id_zamowienia

        if db is not None:
            return _submit(db)
        with transactional_session() as session:
            return _submit(session)

    @staticmethod
    def list_orders(
        filter_user_id: Optional[int] = None, db: Optional[Session] = None
    ) -> list[dict]:
        def _list(session: Session):
            query = session.query(PartOrder)

            if filter_user_id is not None:
                query = query.filter(PartOrder.id_skladajacego == filter_user_id)

            query = query.order_by(PartOrder.data_zlozenia.desc())

            orders = query.all()
            result = []
            for o in orders:
                item = o.pozycje[0] if o.pozycje else None
                part_name = (
                    item.czesc.nazwa_czesci if item and item.czesc else "Brak pozycji"
                )
                qty = item.ilosc if item else 0

                result.append(
                    {
                        "id_zamowienia": o.id_zamowienia,
                        "id_skladajacego": o.id_skladajacego,
                        "zamawiajacy": (
                            f"{o.skladajacy.imie} {o.skladajacy.nazwisko}"
                            if o.skladajacy
                            else "Nieznany"
                        ),
                        "status_id": o.status_zamowienia,
                        "status_nazwa": (
                            o.status.nazwa_statusu
                            if o.status
                            else str(o.status_zamowienia)
                        ),
                        "data_zamowienia": (
                            o.data_zlozenia.strftime("%Y-%m-%d %H:%M")
                            if o.data_zlozenia
                            else ""
                        ),
                        "nazwa_czesci": part_name,
                        "ilosc": qty,
                        "typ_czesci_id": (
                            item.czesc.typ_czesci if item and item.czesc else None
                        ),
                    }
                )
            return result

        if db is not None:
            return _list(db)
        with transactional_session() as session:
            return _list(session)

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

            # Mapowanie nazw statusow
            status_map = {
                "oczekujace na zatwierdzenie": "Do zatwierdzenia",
                "do zatwierdzenia": "Do zatwierdzenia",
                "zatwierdzone": "Zatwierdzone",
                "odrzucone": "Odrzucone",
                "zrealizowane": "Dostarczone",
                "dostarczone": "Dostarczone",
                "w realizacji": "W realizacji",
            }
            db_status_name = status_map.get(status_name.lower(), status_name)

            status = (
                session.query(OrderPartsStatus)
                .filter(OrderPartsStatus.nazwa_statusu == db_status_name)
                .first()
            )
            if not status:
                status = (
                    session.query(OrderPartsStatus)
                    .filter(OrderPartsStatus.nazwa_statusu == status_name)
                    .first()
                )

            if not status:
                raise ValueError(
                    f"Nie znaleziono statusu '{status_name}' (szukano: {db_status_name})"
                )

            # Aktualizacja stanu magazynowego przy dostarczeniu
            # Sprawdzamy, czy nowy status to "Dostarczone"
            is_new_delivered = status.nazwa_statusu == "Dostarczone"

            current_status_name = order.status.nazwa_statusu if order.status else ""
            is_current_delivered = current_status_name == "Dostarczone"

            if is_new_delivered and not is_current_delivered:
                # Zwiekszamy ilosc dostepna dla wszystkich czesci w zamowieniu
                for item in order.pozycje:
                    part = session.get(Part, item.id_czesci)
                    if part:
                        part.ilosc_dostepna = (part.ilosc_dostepna or 0) + item.ilosc

            order.status_zamowienia = status.id_statusu

            if zatwierdzajacy_id and db_status_name in ["Zatwierdzone", "Odrzucone"]:
                order.id_zatwierdzajacego = zatwierdzajacy_id

            if db_status_name == "Zatwierdzone":
                order.data_zatwierdzenia = datetime.now(timezone.utc)
            elif db_status_name == "Dostarczone":
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
    def get_order_details(order_id: int, db: Optional[Session] = None) -> dict:
        def _get(session: Session) -> dict:
            order = session.get(PartOrder, order_id)
            if not order:
                raise ValueError("Zamówienie nie istnieje")
            items = order.pozycje
            return {
                "id_zamowienia": order.id_zamowienia,
                "id_skladajacego": order.id_skladajacego,
                "id_zatwierdzajacego": order.id_zatwierdzajacego,
                "status_zamowienia": order.status.nazwa_statusu if order.status else "",
                "data_zlozenia": (
                    order.data_zlozenia.isoformat() if order.data_zlozenia else None
                ),
                "pozycje": [
                    {
                        "id_pozycji": it.id_pozycji,
                        "id_czesci": it.id_czesci,
                        "nazwa_czesci": it.czesc.nazwa_czesci,
                        "ilosc": it.ilosc,
                        "cena_jednostkowa": (
                            float(it.cena_jednostkowa) if it.cena_jednostkowa else 0.0
                        ),
                    }
                    for it in items
                ],
            }

        if db is not None:
            return _get(db)
        with transactional_session() as session:
            return _get(session)

    @staticmethod
    def delete_item(order_id: int, item_id: int, db: Optional[Session] = None) -> None:
        def _del(session: Session) -> None:
            it = session.get(OrderItem, item_id)
            if it and it.id_zamowienia == order_id:
                session.delete(it)

        if db is not None:
            _del(db)
        with transactional_session() as session:
            _del(session)

    @staticmethod
    def delete_order(order_id: int, db: Optional[Session] = None) -> None:
        def _del(session: Session) -> None:
            order = session.get(PartOrder, order_id)
            if not order:
                return
            for item in order.pozycje:
                session.delete(item)
            session.delete(order)

        if db is not None:
            _del(db)
        with transactional_session() as session:
            _del(session)

    @staticmethod
    def create_order(skladajacy_id: int, db: Optional[Session] = None) -> int:
        def _create(session: Session) -> int:
            status = (
                session.query(OrderPartsStatus)
                .filter(OrderPartsStatus.nazwa_statusu == "Do zatwierdzenia")
                .first()
            )
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
    def approve(
        order_id: int, zatwierdzajacy_id: int, db: Optional[Session] = None
    ) -> dict:
        return PartsOrderService.change_status(
            order_id, "Zatwierdzone", zatwierdzajacy_id, db
        )

    @staticmethod
    def reject(
        order_id: int, zatwierdzajacy_id: int, db: Optional[Session] = None
    ) -> dict:
        return PartsOrderService.change_status(
            order_id, "Odrzucone", zatwierdzajacy_id, db
        )

    @staticmethod
    def receive(order_id: int, db: Optional[Session] = None) -> dict:
        # Metoda receive teraz po prostu zmienia status, a change_status obsluzy logike magazynowa
        return PartsOrderService.change_status(order_id, "Dostarczone", db=db)
