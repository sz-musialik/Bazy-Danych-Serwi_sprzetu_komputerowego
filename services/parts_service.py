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
    ) -> int:

        def _create(db_sess: Session) -> int:
            part = Part(
                nazwa_czesci=nazwa_czesci,
                typ_czesci=typ_czesci,
                producent=producent,
                numer_katalogowy=numer_katalogowy,
                cena_katalogowa=cena_katalogowa,
                ilosc_dostepna=ilosc_dostepna,
            )
            db_sess.add(part)
            db_sess.flush()
            validate_part(part)
            return part.id_czesci

        if db is not None:
            return _create(db)

        with transactional_session() as session:
            return _create(session)

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
    ) -> None:

        def _update(db_sess: Session) -> None:
            part = db_sess.get(Part, part_id)
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

            db_sess.flush()
            validate_part(part)

        if db is not None:
            _update(db)
            return

        with transactional_session() as session:
            _update(session)

    @staticmethod
    def get_part(part_id: int, db: Optional[Session] = None) -> Optional[dict]:

        def _serialize(p: Part) -> dict:
            return {
                "id_czesci": p.id_czesci,
                "nazwa_czesci": p.nazwa_czesci,
                "typ_czesci": p.typ_czesci,
                "producent": p.producent,
                "numer_katalogowy": p.numer_katalogowy,
                "cena_katalogowa": p.cena_katalogowa,
                "ilosc_dostepna": p.ilosc_dostepna,
            }

        if db is not None:
            part = db.get(Part, part_id)
            return _serialize(part) if part else None

        with transactional_session() as session:
            part = session.get(Part, part_id)
            return _serialize(part) if part else None

    @staticmethod
    def list_parts(db: Optional[Session] = None) -> List[dict]:

        def _serialize(parts: list[Part]) -> list[dict]:
            return [
                {
                    "id_czesci": p.id_czesci,
                    "nazwa_czesci": p.nazwa_czesci,
                    "typ_czesci": p.typ_czesci,
                    "producent": p.producent,
                    "numer_katalogowy": p.numer_katalogowy,
                    "cena_katalogowa": p.cena_katalogowa,
                    "ilosc_dostepna": p.ilosc_dostepna,
                }
                for p in parts
            ]

        if db is not None:
            return _serialize(db.query(Part).all())

        with transactional_session() as session:
            return _serialize(session.query(Part).all())

    @staticmethod
    def update_stock(
        part_id: int,
        ilosc_zmiana: int,
        db: Optional[Session] = None,
    ) -> None:

        def _update(db_sess: Session) -> None:
            part = (
                db_sess.query(Part)
                .filter(Part.id_czesci == part_id)
                .with_for_update()
                .first()
            )

            if not part:
                raise ValueError(f"Nie znaleziono czesci o id={part_id}")

            new_stock = part.ilosc_dostepna + ilosc_zmiana
            if new_stock < 0:
                raise ValueError("Nie mozna ustawic ujemnego stanu magazynowego.")

            part.ilosc_dostepna = new_stock
            db_sess.flush()
            validate_part(part)

        if db is not None:
            _update(db)
            return

        with transactional_session() as session:
            _update(session)
