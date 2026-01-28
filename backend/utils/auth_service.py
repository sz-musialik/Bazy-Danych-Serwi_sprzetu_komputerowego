from typing import Optional
from sqlalchemy.orm import Session
from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)
from backend.models.user import User
from backend.models.role import Role


class AuthService:

    @staticmethod
    def hash_password(password: str) -> str:
        return generate_password_hash(password)

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        # W check_password_hash kolejnosc to (hash, haslo_jawne)
        return check_password_hash(hashed, password)

    @staticmethod
    def create_user(
        db: Session,
        imie: str,
        nazwisko: str,
        login: str,
        haslo: str,
        email: str | None = None,
        nr_telefonu: str | None = None,
        rola_id: int = 3,
    ) -> User:

        if not login or not haslo:
            raise ValueError("login i haslo sa wymagane")

        hashed_password = AuthService.hash_password(haslo)

        user = User(
            imie=imie,
            nazwisko=nazwisko,
            login=login,
            haslo_hash=hashed_password,
            email=email,
            nr_telefonu=nr_telefonu,
            rola_uzytkownika=rola_id,
            czy_aktywny=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def authenticate(db: Session, login: str, password: str) -> Optional[User]:
        user = db.query(User).filter(User.login == login).first()

        if user is None:
            return None

        if user.czy_aktywny is False:
            return None

        if not AuthService.verify_password(password, user.haslo_hash):
            return None

        return user

    @staticmethod
    def get_user_role_name(db: Session, user: User) -> str:
        role = db.query(Role).filter(Role.id_rola == user.rola_uzytkownika).first()

        if role is None:
            raise ValueError(f"Nie znaleziono roli o id={user.rola_uzytkownika}")

        return role.nazwa_rola
