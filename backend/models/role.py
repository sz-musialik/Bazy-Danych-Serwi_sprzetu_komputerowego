from sqlalchemy import Column, Integer, String
from backend.database import Base


class Role(Base):
    __tablename__ = "role"

    id_rola = Column(Integer, primary_key=True, autoincrement=True)
    nazwa_rola = Column(String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"<Role(id={self.id_rola}, nazwa='{self.nazwa_rola}')>"
