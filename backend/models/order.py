from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class Order(Base):
    __tablename__ = "zlecenia_naprawy"

    id_zlecenia = Column(Integer, primary_key=True, autoincrement=True)
    id_klienta = Column(Integer, ForeignKey("klienci.id_klienta"), nullable=False)
    id_pracownika = Column(
        Integer, ForeignKey("uzytkownicy.id_uzytkownika"), nullable=False
    )
    typ_sprzetu = Column(Integer, ForeignKey("typy_sprzetu.id_typu"), nullable=False)
    data_rozpoczecia = Column(DateTime, default=datetime.utcnow)
    data_zakonczenia = Column(DateTime, nullable=True)
    opis_usterki = Column(String(2000), nullable=True)
    status_zlecenia = Column(
        Integer, ForeignKey("statusy_zlecen.id_statusu"), nullable=False
    )
    koszt_robocizny = Column(Numeric(10, 2), default=0.00)
    koszt_czesci = Column(Numeric(10, 2), default=0.00)
    marka_sprzetu = Column(String(255), nullable=True)
    model_sprzetu = Column(String(255), nullable=True)
    numer_seryjny = Column(String(50), nullable=True)
    diagnoza = Column(String(255), nullable=True)
    wykonane_czynnosci = Column(String(255), nullable=True)

    klient = relationship("Client", back_populates="zlecenia")
    pracownik = relationship("User")
    typ_sprzetu_obj = relationship("EquipmentType", back_populates="zlecenia")
    status = relationship("OrderStatus")

    wykorzystane_czesci = relationship("PartsUsed", back_populates="zlecenie")

    def __repr__(self):
        return f"<Order(id={self.id_zlecenia}, klient_id={self.id_klienta}, pracownik_id={self.id_pracownika}, typ_sprzetu={self.typ_sprzetu})>"
