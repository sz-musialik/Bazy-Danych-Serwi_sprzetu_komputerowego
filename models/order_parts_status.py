from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.database import Base


class OrderPartsStatus(Base):
    __tablename__ = "statusy_zamowien"

    id_statusu = Column(Integer, primary_key=True, autoincrement=True)
    nazwa_statusu = Column(String(100), nullable=False, unique=True)

    zamowienia = relationship("PartOrder", back_populates="status")

    def __repr__(self):
        return f"<OrderPartsStatus(id={self.id_statusu}, nazwa='{self.nazwa_statusu}')>"
