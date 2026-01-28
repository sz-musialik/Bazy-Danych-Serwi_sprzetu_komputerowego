from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from backend.database import Base
from sqlalchemy.orm import relationship


class Part(Base):
    __tablename__ = "czesci"

    id_czesci = Column(Integer, primary_key=True, index=True)
    nazwa_czesci = Column(String(100), nullable=False)

    # Klucz obcy do typy_czesci
    typ_czesci = Column(Integer, ForeignKey("typy_czesci.id_typu"), nullable=False)

    producent = Column(String(100))
    numer_katalogowy = Column(String(100))
    cena_katalogowa = Column(Numeric(10, 2))
    ilosc_dostepna = Column(Integer, default=0)

    wykorzystane = relationship("PartsUsed", back_populates="czesc")
    pozycje_zamowienia = relationship("OrderItem", back_populates="czesc")

    def __repr__(self):
        return f"<Part(id={self.id_czesci}, nazwa='{self.nazwa_czesci}', ilosc={self.ilosc_dostepna})>"
