from typing import Optional
from datetime import datetime, timezone
from backend.db.session import transactional_session
from backend.models.order import Order
from backend.models.client import Client
from backend.models.equipment_type import EquipmentType
from sqlalchemy.orm import Session
from backend.validations.output_validators import validate_order

class OrderService:
    def create_order(self, actor_user, client_id: int, equipment_type_id: int, description: str, db: Optional[Session] = None):

        if db is not None:
            client = db.get(Client, client_id)
            equipment_type = db.get(EquipmentType, equipment_type_id)
            if not client or not equipment_type:
                raise ValueError("Nieprawidlowe dane klienta/sprzetu")

            if not (getattr(actor_user,'is_admin',False) or getattr(actor_user,'is_manager',False)):
                owner_id = getattr(client, 'owner_id', None)
                if owner_id is not None and owner_id != getattr(actor_user, 'id_uzytkownika', None):
                    raise PermissionError("Brak widocznosci klienta")
            order = Order(
                id_klienta=client.id_klienta,
                id_pracownika=getattr(actor_user, 'id_uzytkownika', None),
                typ_sprzetu=equipment_type.id_typu,
                opis_usterki=description,
                data_rozpoczecia=datetime.now(timezone.utc),
                status_zlecenia=1,
            )
            db.add(order)
            db.flush()
            db.refresh(order)
            validate_order(order)
            return order.id_zlecenia

        with transactional_session() as session:
            client = session.get(Client, client_id)
            equipment_type = session.get(EquipmentType, equipment_type_id)
            if not client or not equipment_type:
                raise ValueError("Nieprawidlowe dane klienta/sprzetu")
            if not (getattr(actor_user,'is_admin',False) or getattr(actor_user,'is_manager',False)):
                owner_id = getattr(client, 'owner_id', None)
                if owner_id is not None and owner_id != getattr(actor_user, 'id_uzytkownika', None):
                    raise PermissionError("Brak widocznosci klienta")
            order = Order(
                id_klienta=client.id_klienta,
                id_pracownika=getattr(actor_user, 'id_uzytkownika', None),
                typ_sprzetu=equipment_type.id_typu,
                opis_usterki=description,
                data_rozpoczecia=datetime.now(timezone.utc),
                status_zlecenia=1,
            )
            session.add(order)
            session.flush()
            session.refresh(order)
            validate_order(order)
            return order.id_zlecenia

    def change_status(self, actor_user, order_id: int, new_status: int, db: Optional[Session] = None):
        if db is not None:
            order = db.get(Order, order_id)
            if not order:
                raise ValueError("Brak zlecenia")
            if not (getattr(actor_user,'is_manager',False) or order.id_pracownika == getattr(actor_user,'id_uzytkownika',None)):
                raise PermissionError("Brak uprawnien")
            order.status_zlecenia = new_status
            db.flush()
            return

        with transactional_session() as session:
            order = session.get(Order, order_id)
            if not order:
                raise ValueError("Brak zlecenia")
            if not (getattr(actor_user,'is_manager',False) or order.id_pracownika == getattr(actor_user,'id_uzytkownika',None)):
                raise PermissionError("Brak uprawnien")
            order.status_zlecenia = new_status
            session.add(order)
