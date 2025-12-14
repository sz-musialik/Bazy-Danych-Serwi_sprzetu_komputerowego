from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class User(Base):
    __tablename__ = "uzytkownicy"

    id_uzytkownika = Column(Integer, primary_key=True, autoincrement=True)
    imie = Column(String(255), nullable=False)
    nazwisko = Column(String(255), nullable=False)
    login = Column(String(255), unique=True, nullable=False)
    haslo_hash = Column(String(255), nullable=False)
    email = Column(String(255), unique=True)
    nr_telefonu = Column(String(20))
    rola_uzytkownika = Column(Integer, ForeignKey("role.id_rola"))
    czy_aktywny = Column(Boolean, default=True)

    role = relationship("Role")
    # relacja do danych kadrowych (1:1)
    dane_kadrowe = relationship("EmployeeData", back_populates="uzytkownik", uselist=False)

    def __repr__(self):
        return f"<User(id={self.id_uzytkownika}, login='{self.login}', rola={self.rola_uzytkownika})>"
