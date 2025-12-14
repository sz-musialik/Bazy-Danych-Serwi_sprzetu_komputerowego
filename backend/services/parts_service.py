from typing import Optional, List
from sqlalchemy.orm import Session
from backend.models.parts import Part
from backend.db.session import transactional_session
from backend.validations.output_validators import validate_part


class PartsService:
    @staticmethod
    def add_part(
        nazwa_czesci: str,
        typ_czesci: int | None = None,
        producent: str | None = None,
        numer_katalogowy: str | None = None,
        cena_katalogowa: float | None = None,
        ilosc_dostepna: int = 0,
        db: Optional[Session] = None,
    ) -> Part:

        part = Part(
            nazwa_czesci=nazwa_czesci,
            typ_czesci=typ_czesci,
            producent=producent,
            numer_katalogowy=numer_katalogowy,
            cena_katalogowa=cena_katalogowa,
            ilosc_dostepna=ilosc_dostepna,
        )

        if db is not None:
            db.add(part)
            db.flush()
            db.refresh(part)
            validate_part(part)
            return part

        with transactional_session() as db_sess:
            db_sess.add(part)
            db_sess.flush()
            db_sess.refresh(part)
            validate_part(part)
            return part

    @staticmethod
    def update_part(
        part_id: int,
        nazwa_czesci: str | None = None,
        typ_czesci: int | None = None,
        producent: str | None = None,
        numer_katalogowy: str | None = None,
        cena_katalogowa: float | None = None,
        ilosc_dostepna: int | None = None,
        db: Optional[Session] = None,
    ) -> Part:

        if db is not None:
            part = db.query(Part).filter(Part.id_czesci == part_id).first()
        else:
            with transactional_session() as db_sess:
                part = db_sess.query(Part).filter(Part.id_czesci == part_id).first()

        if not part:
            raise ValueError(f"Nie znaleziono czesci o id={part_id}")

        if nazwa_czesci is not None:
            part.nazwa_czesci = nazwa_czesci

        if typ_czesci is not None:
            part.typ_czesci = typ_czesci

        if producent is not None:
            part.producent = producent

        if numer_katalogowy is not None:
            part.numer_katalogowy = numer_katalogowy

        if cena_katalogowa is not None:
            part.cena_katalogowa = cena_katalogowa

        if ilosc_dostepna is not None:
            if ilosc_dostepna < 0:
                raise ValueError("Nie mozna ustawic ujemnego stanu magazynowego.")
            part.ilosc_dostepna = ilosc_dostepna

        if db is not None:
            db.flush()
            db.refresh(part)
            validate_part(part)
            return part

        with transactional_session() as db_sess:
            db_sess.add(part)
            db_sess.flush()
            db_sess.refresh(part)
            validate_part(part)
            return part

    @staticmethod
    def get_part(part_id: int, db: Optional[Session] = None) -> Optional[Part]:
        if db is not None:
            return db.query(Part).filter(Part.id_czesci == part_id).first()
        with transactional_session() as db_sess:
            return db_sess.query(Part).filter(Part.id_czesci == part_id).first()

    @staticmethod
    def list_parts(db: Optional[Session] = None) -> List[Part]:
        if db is not None:
            return db.query(Part).all()
        with transactional_session() as db_sess:
            return db_sess.query(Part).all()

    @staticmethod
    def update_stock(part_id: int, ilosc_zmiana: int, db: Optional[Session] = None) -> Part:
        if db is not None:
            part = db.query(Part).filter(Part.id_czesci == part_id).with_for_update().first()
            if not part:
                raise ValueError(f"Nie znaleziono czesci o id={part_id}")
            new_stock = part.ilosc_dostepna + ilosc_zmiana
            if new_stock < 0:
                raise ValueError("Nie mozna ustawic ujemnego stanu magazynowego.")
            part.ilosc_dostepna = new_stock
            db.flush()
            db.refresh(part)
            validate_part(part)
            return part

        with transactional_session() as db_sess:
            part = db_sess.query(Part).filter(Part.id_czesci == part_id).with_for_update().first()

            if not part:
                raise ValueError(f"Nie znaleziono czesci o id={part_id}")

            new_stock = part.ilosc_dostepna + ilosc_zmiana
            if new_stock < 0:
                raise ValueError("Nie mozna ustawic ujemnego stanu magazynowego.")

            part.ilosc_dostepna = new_stock
            db_sess.flush()
            db_sess.refresh(part)
            validate_part(part)
            return part
