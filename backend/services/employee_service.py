from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.employee_data import EmployeeData
from models.user import User


class EmployeeService:
    @staticmethod
    def create_employee_data(
        db: Session,
        user_id: int,
        pesel: str,
        nr_konta: str | None = None,
        adres_zamieszkania: str | None = None,
        stawka_godzinowa: float | None = None,
        data_zatrudnienia=None,
    ) -> EmployeeData:

        user = db.query(User).filter(User.id_uzytkownika == user_id).first()
        if not user:
            raise ValueError("Użytkownik o podanym ID nie istnieje.")

        existing = (
            db.query(EmployeeData)
            .filter(EmployeeData.id_uzytkownika == user_id)
            .first()
        )
        if existing:
            raise ValueError("Dane kadrowe dla tego użytkownika już istnieją.")

        employee_data = EmployeeData(
            id_uzytkownika=user_id,
            pesel=pesel,
            nr_konta=nr_konta,
            adres_zamieszkania=adres_zamieszkania,
            stawka_godzinowa=stawka_godzinowa,
            data_zatrudnienia=data_zatrudnienia,
        )

        try:
            db.add(employee_data)
            db.commit()
            db.refresh(employee_data)
            return employee_data

        except IntegrityError:
            db.rollback()
            raise ValueError("Podany PESEL już istnieje w bazie.")

    @staticmethod
    def update_employee_data(
        db: Session,
        user_id: int,
        pesel: str | None = None,
        nr_konta: str | None = None,
        adres_zamieszkania: str | None = None,
        stawka_godzinowa: float | None = None,
        data_zatrudnienia=None,
    ) -> bool:

        employee = (
            db.query(EmployeeData)
            .filter(EmployeeData.id_uzytkownika == user_id)
            .first()
        )
        if not employee:
            return False

        if pesel is not None:
            employee.pesel = pesel
        if nr_konta is not None:
            employee.nr_konta = nr_konta
        if adres_zamieszkania is not None:
            employee.adres_zamieszkania = adres_zamieszkania
        if stawka_godzinowa is not None:
            employee.stawka_godzinowa = stawka_godzinowa
        if data_zatrudnienia is not None:
            employee.data_zatrudnienia = data_zatrudnienia

        db.commit()
        return True

    @staticmethod
    def get_employee_data(db: Session, user_id: int) -> EmployeeData | None:
        return (
            db.query(EmployeeData)
            .filter(EmployeeData.id_uzytkownika == user_id)
            .first()
        )

    @staticmethod
    def get_all_employees(db: Session) -> list[EmployeeData]:
        return db.query(EmployeeData).order_by(EmployeeData.id_uzytkownika).all()
