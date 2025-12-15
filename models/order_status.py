from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.database import Base


class OrderStatus(Base):
    __tablename__ = "statusy_zlecen"

    id_statusu = Column(Integer, primary_key=True, autoincrement=True)
    nazwa_statusu = Column(String(100), nullable=False, unique=True)

    zlecenia = relationship("Order", back_populates="status")

    def __repr__(self):
        return f"<OrderStatus(id={self.id_statusu}, nazwa='{self.nazwa_statusu}')>"
