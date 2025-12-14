from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class Client(Base):
    __tablename__ = "klienci"

    id_klienta = Column(Integer, primary_key=True, autoincrement=True)
    imie = Column(String(255), nullable=True)
    nazwisko = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True, unique=True)
    nr_telefonu = Column(String(20), nullable=True)
    adres = Column(String(255), nullable=True)
    data_rejestracji = Column(DateTime, default=datetime.utcnow)
    czy_aktywny = Column(Boolean, default=True)
    zlecenia = relationship("Order", back_populates="klient")

    def __repr__(self):
        return f"<Client(id={self.id_klienta}, imie='{self.imie}', nazwisko='{self.nazwisko}')>"
