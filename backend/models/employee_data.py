from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class EmployeeData(Base):
    __tablename__ = "dane_kadrowe"

    id_uzytkownika = Column(
        Integer, ForeignKey("uzytkownicy.id_uzytkownika"), primary_key=True
    )
    pesel = Column(String(11), nullable=False, unique=True)
    nr_konta = Column(String(26), nullable=True)
    adres_zamieszkania = Column(String(255), nullable=True)
    stawka_godzinowa = Column(Numeric(10, 2), nullable=True)
    data_zatrudnienia = Column(Date, nullable=True)

    # relacja do użytkownika
    uzytkownik = relationship("User", back_populates="dane_kadrowe")

    def __repr__(self):
        return (
            f"<EmployeeData(uzytkownik_id={self.id_uzytkownika}, pesel={self.pesel})>"
        )
