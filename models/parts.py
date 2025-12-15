from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import relationship
from backend.database import Base


class Part(Base):
    __tablename__ = "czesci"

    id_czesci = Column(Integer, primary_key=True, autoincrement=True)
    nazwa_czesci = Column(String(255), nullable=False)
    typ_czesci = Column(Integer, nullable=True)
    producent = Column(String(255), nullable=True)
    numer_katalogowy = Column(String(50), nullable=True)
    cena_katalogowa = Column(Numeric(10, 2), nullable=True)
    ilosc_dostepna = Column(Integer, default=0)

    wykorzystane = relationship("PartsUsed", back_populates="czesc")
    pozycje_zamowienia = relationship("OrderItem", back_populates="czesc")

    def __repr__(self):
        return f"<Part(id={self.id_czesci}, nazwa='{self.nazwa_czesci}', ilosc={self.ilosc_dostepna})>"
