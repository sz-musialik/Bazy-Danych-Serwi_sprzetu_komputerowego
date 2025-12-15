from typing import Optional, List
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.models.client import Client
from backend.db.session import transactional_session
from backend.validations.output_validators import validate_client


class ClientService:

    @staticmethod
    def create_client(
        imie: str,
        nazwisko: str,
        email: str,
        nr_telefonu: str,
        adres: str,
        db: Optional[Session] = None,
    ) -> int:

        if not all([imie, nazwisko, email, nr_telefonu, adres]):
            raise ValueError("Wszystkie pola klienta są wymagane")

        client = Client(
            imie=imie,
            nazwisko=nazwisko,
            email=email,
            nr_telefonu=nr_telefonu,
            adres=adres,
        )

        validate_client(client)

        try:
            if db is not None:
                db.add(client)
                db.flush()
                return client.id_klienta

            with transactional_session() as session:
                session.add(client)
                session.flush()
                return client.id_klienta

        except IntegrityError:
            raise ValueError("Klient o podanym emailu już istnieje.")

    @staticmethod
    def update_client(
        client_id: int,
        imie: str | None = None,
        nazwisko: str | None = None,
        email: str | None = None,
        nr_telefonu: str | None = None,
        adres: str | None = None,
        db: Optional[Session] = None,
    ) -> bool:

        def _update(session: Session) -> bool:
            client = session.get(Client, client_id)
            if not client:
                return False

            if imie is not None:
                client.imie = imie
            if nazwisko is not None:
                client.nazwisko = nazwisko
            if email is not None:
                client.email = email
            if nr_telefonu is not None:
                client.nr_telefonu = nr_telefonu
            if adres is not None:
                client.adres = adres

            validate_client(client)
            session.flush()
            return True

        try:
            if db is not None:
                return _update(db)

            with transactional_session() as session:
                return _update(session)

        except IntegrityError:
            raise ValueError("Klient o podanym emailu już istnieje.")

    @staticmethod
    def get_client_by_id(
        client_id: int,
        db: Optional[Session] = None,
    ) -> Optional[Client]:

        if db is not None:
            return db.get(Client, client_id)

        with transactional_session() as session:
            return session.get(Client, client_id)

    @staticmethod
    def get_all_clients(db: Optional[Session] = None) -> List[dict]:

        def serialize(c: Client) -> dict:
            return {
                "id_klienta": c.id_klienta,
                "imie": c.imie,
                "nazwisko": c.nazwisko,
                "email": c.email,
                "nr_telefonu": c.nr_telefonu,
                "adres": c.adres,
                "data_rejestracji": c.data_rejestracji.isoformat() if c.data_rejestracji else None,
            }

        def _query(session: Session) -> List[dict]:
            return [serialize(c) for c in session.query(Client).order_by(Client.id_klienta).all()]

        if db is not None:
            return _query(db)

        with transactional_session() as session:
            return _query(session)
