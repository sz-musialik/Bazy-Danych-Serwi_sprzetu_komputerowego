from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class PartsUsed(Base):
    __tablename__ = "czesci_wykorzystane"

    id_pozycji = Column(Integer, primary_key=True, autoincrement=True)
    id_zlecenia = Column(
        Integer, ForeignKey("zlecenia_naprawy.id_zlecenia"), nullable=False
    )
    id_czesci = Column(Integer, ForeignKey("czesci.id_czesci"), nullable=False)
    ilosc = Column(Integer, nullable=False)
    cena_jednostkowa = Column(Numeric(10, 2), nullable=False)
    data_wykorzystania = Column(DateTime, default=datetime.utcnow)

    zlecenie = relationship("Order", back_populates="wykorzystane_czesci")
    czesc = relationship("Part", back_populates="wykorzystane")

    def __repr__(self):
        return f"<PartsUsed(id={self.id_pozycji}, zlecenie_id={self.id_zlecenia}, czesc_id={self.id_czesci}, ilosc={self.ilosc})>"
