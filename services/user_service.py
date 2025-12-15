from backend.utils.auth_service import AuthService
from backend.db.session import transactional_session
from backend.models.user import User
from backend.models.role import Role

class UserService:
    def create_user(self, username: str, password: str, created_by_id: int):
        if not username or not password:
            raise ValueError("username i password wymagane")
        hashed = AuthService.hash_password(password)
        with transactional_session() as session:
            if session.query(User).filter_by(login=username).first():
                raise ValueError("uzytkownik istnieje")
            user = User(login=username, haslo_hash=hashed)
            session.add(user)
            session.flush()
            return user.id_uzytkownika

    def set_archived(self, actor_user, user_id: int, archived: bool):
        if not getattr(actor_user, 'is_admin', False):
            raise PermissionError("Brak uprawnień")
        with transactional_session() as session:
            user = session.get(User, user_id)
            if not user:
                raise ValueError("Brak uzytkownika")
            user.czy_aktywny = not archived
            session.add(user)

    def assign_role(self, actor_user, user_id: int, role_name: str):
        if not getattr(actor_user, 'is_admin', False):
            raise PermissionError("Brak uprawnień")
        with transactional_session() as session:
            user = session.get(User, user_id)
            role = session.query(Role).filter_by(nazwa_rola=role_name).first()
            if not user or not role:
                raise ValueError("Nie znaleziono")
            user.rola_uzytkownika = role.id_rola
            session.add(user)