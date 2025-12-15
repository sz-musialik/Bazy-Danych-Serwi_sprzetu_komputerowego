from sqlalchemy import Column, Integer, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from backend.database import Base


class OrderItem(Base):
    __tablename__ = "pozycje_zamowienia"

    id_pozycji = Column(Integer, primary_key=True, autoincrement=True)
    id_zamowienia = Column(
        Integer, ForeignKey("zamowienia_czesci.id_zamowienia"), nullable=False
    )
    id_czesci = Column(Integer, ForeignKey("czesci.id_czesci"), nullable=False)
    ilosc = Column(Integer, nullable=False)
    cena_jednostkowa = Column(Numeric(10, 2), nullable=True)

    zamowienie = relationship("PartOrder", back_populates="pozycje")
    czesc = relationship("Part", back_populates="pozycje_zamowienia")

    def __repr__(self):
        return f"<OrderItem(id={self.id_pozycji}, zamowienie_id={self.id_zamowienia}, czesc_id={self.id_czesci}, ilosc={self.ilosc})>"
