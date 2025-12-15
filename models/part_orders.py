from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class PartOrder(Base):
    __tablename__ = "zamowienia_czesci"

    id_zamowienia = Column(Integer, primary_key=True, autoincrement=True)
    id_skladajacego = Column(
        Integer, ForeignKey("uzytkownicy.id_uzytkownika"), nullable=False
    )
    id_zatwierdzajacego = Column(
        Integer, ForeignKey("uzytkownicy.id_uzytkownika"), nullable=True
    )
    data_zlozenia = Column(DateTime, default=datetime.utcnow)
    data_zatwierdzenia = Column(DateTime, nullable=True)
    data_realizacji = Column(DateTime, nullable=True)
    status_zamowienia = Column(
        Integer, ForeignKey("statusy_zamowien.id_statusu"), nullable=False
    )

    skladajacy = relationship("User", foreign_keys=[id_skladajacego])
    zatwierdzajacy = relationship("User", foreign_keys=[id_zatwierdzajacego])
    status = relationship("OrderPartsStatus", back_populates="zamowienia")
    pozycje = relationship("OrderItem", back_populates="zamowienie")

    def __repr__(self):
        return f"<PartOrder(id={self.id_zamowienia}, skladajacy_id={self.id_skladajacego}, status={self.status_zamowienia})>"
