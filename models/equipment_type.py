from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.database import Base


class EquipmentType(Base):
    __tablename__ = "typy_sprzetu"

    id_typu = Column(Integer, primary_key=True, autoincrement=True)
    nazwa_typu = Column(String(255), nullable=False, unique=True)

    zlecenia = relationship("Order", back_populates="typ_sprzetu_obj")

    def __repr__(self):
        return f"<EquipmentType(id={self.id_typu}, nazwa='{self.nazwa_typu}')>"
