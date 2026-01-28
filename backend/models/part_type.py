from sqlalchemy import Column, Integer, String
from backend.database import Base


class PartType(Base):
    __tablename__ = "typy_czesci"

    id_typu = Column(Integer, primary_key=True, index=True)
    nazwa_typu = Column(String(50), unique=True, nullable=False)
