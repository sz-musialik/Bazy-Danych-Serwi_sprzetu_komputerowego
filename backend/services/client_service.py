from typing import Optional, List
from backend.models.client import Client
from backend.db.session import transactional_session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from backend.validations.output_validators import validate_client


class ClientService:
    @staticmethod
    def create_client(
            nazwa: str,
            adres: str | None = None,
            email: str | None = None,
            telefon: str | None = None,
            nip: str | None = None,
            db: Optional[Session] = None,
    ) -> int:

        client = Client(
            imie=nazwa,
            adres=adres,
            email=email,
            nr_telefonu=telefon,
        )
        validate_client(client)
        try:
            if db is not None:
                db.add(client)
                db.flush()
                client_id = client.id_klienta
                #validate_client(client)
                return client_id

            with transactional_session() as db_sess:
                db_sess.add(client)
                db_sess.flush()
                client_id = client.id_klienta
                validate_client(client)
                return client_id

        except IntegrityError:
            raise ValueError("Klient o podanym NIP lub email juz istnieje.")

    @staticmethod
    def update_client(
        client_id: int,
        nazwa: str | None = None,
        adres: str | None = None,
        email: str | None = None,
        telefon: str | None = None,
        nip: str | None = None,
        db: Optional[Session] = None,
    ) -> bool:

        if db is not None:
            client = db.query(Client).filter(Client.id_klienta == client_id).first()
            if not client:
                return False

            if nazwa is not None:
                client.imie = nazwa
            if adres is not None:
                client.adres = adres
            if email is not None:
                client.email = email
            if telefon is not None:
                client.nr_telefonu = telefon

            try:
                db.flush()
                db.refresh(client)
                validate_client(client)
                return True
            except IntegrityError:
                raise ValueError("Klient o takim NIP lub email juz istnieje.")

        with transactional_session() as db_sess:
            client = db_sess.query(Client).filter(Client.id_klienta == client_id).first()
            if not client:
                return False

            if nazwa is not None:
                client.imie = nazwa
            if adres is not None:
                client.adres = adres
            if email is not None:
                client.email = email
            if telefon is not None:
                client.nr_telefonu = telefon

            try:
                db_sess.flush()
                db_sess.refresh(client)
                validate_client(client)
                return True
            except IntegrityError:
                raise ValueError("Klient o takim NIP lub email juz istnieje.")

    @staticmethod
    def deactivate_client(client_id: int, db: Optional[Session] = None) -> bool:
        """
        Dezaktywuje klienta zamiast go usuwac.
        """
        if db is not None:
            client = db.query(Client).filter(Client.id_klienta == client_id).first()
            if not client:
                return False

            client.czy_aktywny = False
            db.flush()
            return True

        with transactional_session() as db_sess:
            client = db_sess.query(Client).filter(Client.id_klienta == client_id).first()
            if not client:
                return False

            client.czy_aktywny = False
            return True

    @staticmethod
    def get_client_by_id(client_id: int, db: Optional[Session] = None) -> Optional[Client]:
        if db is not None:
            return db.query(Client).filter(Client.id_klienta == client_id).first()
        with transactional_session() as db_sess:
            return db_sess.query(Client).filter(Client.id_klienta == client_id).first()

    @staticmethod
    def get_all_clients(include_inactive: bool = False, db: Optional[Session] = None) -> List[Client]:
        if db is not None:
            query = db.query(Client)
            if not include_inactive:
                query = query.filter(Client.czy_aktywny == True)
            return query.order_by(Client.id_klienta).all()
        with transactional_session() as db_sess:
            query = db_sess.query(Client)
            if not include_inactive:
                query = query.filter(Client.czy_aktywny == True)
            return query.order_by(Client.id_klienta).all()
