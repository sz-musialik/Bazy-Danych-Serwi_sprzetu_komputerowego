from datetime import datetime
from flask import Blueprint, request, jsonify, g, abort
from werkzeug.security import generate_password_hash
from backend.db.session import transactional_session
from backend.models.user import User
from backend.models.role import Role
from backend.auth.security import require_role
from backend.services.employee_service import EmployeeService

users_bp = Blueprint("users", __name__)


# Tworzenie Uzytkownika
@users_bp.route("/users", methods=["POST"])
@require_role("administrator", "manager")
def create_user():
    payload = request.json or {}
    required_fields = ["login", "password", "imie", "nazwisko"]
    for field in required_fields:
        if field not in payload:
            return jsonify({"error": f"Missing field: {field}"}), 400

    with transactional_session() as session:
        if session.query(User).filter_by(login=payload["login"]).first():
            return jsonify({"error": "Login already exists"}), 409

        requested_role_id = payload.get("rola_id", 3)

        if g.current_role == "manager":
            role_worker = (
                session.query(Role).filter(Role.nazwa_rola == "pracownik").first()
            )
            if role_worker:
                requested_role_id = role_worker.id_rola
            else:
                requested_role_id = 3

        hashed = generate_password_hash(str(payload["password"]))
        user = User(
            imie=payload["imie"],
            nazwisko=payload["nazwisko"],
            login=payload["login"],
            haslo_hash=hashed,
            email=payload.get("email"),
            nr_telefonu=payload.get("nr_telefonu"),
            rola_uzytkownika=requested_role_id,
            czy_aktywny=True,
        )
        session.add(user)
        session.flush()
        return jsonify({"id_uzytkownika": user.id_uzytkownika}), 201


# Pobieranie Listy Uzytkownikow
@users_bp.route("/users", methods=["GET"])
@require_role("administrator", "manager")
def get_users():
    with transactional_session() as session:
        query = session.query(User).order_by(User.id_uzytkownika)

        if g.current_role == "manager":
            query = query.join(Role).filter(Role.nazwa_rola == "pracownik")

        users = query.all()
        roles = session.query(Role).all()
        roles_map = {r.id_rola: r.nazwa_rola for r in roles}

        output = []
        for u in users:
            role_name = roles_map.get(u.rola_uzytkownika, "nieznana")
            emp_data = u.dane_kadrowe

            user_dict = {
                "id_uzytkownika": u.id_uzytkownika,
                "login": u.login,
                "imie": u.imie,
                "nazwisko": u.nazwisko,
                "email": u.email,
                "nr_telefonu": u.nr_telefonu,
                "rola_uzytkownika": u.rola_uzytkownika,
                "rola": role_name,
                "czy_aktywny": u.czy_aktywny,
                "pesel": emp_data.pesel if emp_data else "",
                "nr_konta": emp_data.nr_konta if emp_data else "",
                "adres_zamieszkania": emp_data.adres_zamieszkania if emp_data else "",
                "stawka_godzinowa": (
                    float(emp_data.stawka_godzinowa)
                    if emp_data and emp_data.stawka_godzinowa
                    else 0.0
                ),
                "data_zatrudnienia": (
                    emp_data.data_zatrudnienia.isoformat()
                    if emp_data and emp_data.data_zatrudnienia
                    else None
                ),
            }
            output.append(user_dict)

        return jsonify(output)


# Aktualizacja Danych Uzytkownika
@users_bp.route("/users/<int:user_id>", methods=["PUT"])
@require_role("administrator", "manager")
def update_user(user_id: int):
    data = request.json or {}

    with transactional_session() as session:
        user = session.query(User).filter(User.id_uzytkownika == user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        if g.current_role == "manager":
            user_role_obj = (
                session.query(Role)
                .filter(Role.id_rola == user.rola_uzytkownika)
                .first()
            )
            if not user_role_obj or user_role_obj.nazwa_rola != "pracownik":
                return (
                    jsonify({"error": "Forbidden: Managers can only edit employees"}),
                    403,
                )
            if "rola_uzytkownika" in data:
                del data["rola_uzytkownika"]

        user.imie = data.get("imie", user.imie)
        user.nazwisko = data.get("nazwisko", user.nazwisko)
        user.email = data.get("email", user.email)
        user.nr_telefonu = data.get("nr_telefonu", user.nr_telefonu)

        if "rola_uzytkownika" in data:
            user.rola_uzytkownika = int(data["rola_uzytkownika"])

        if "czy_aktywny" in data:
            user.czy_aktywny = bool(data["czy_aktywny"])

        if "password" in data and data["password"]:
            hashed = generate_password_hash(str(data["password"]))
            user.haslo_hash = hashed

        # Obsluga danych kadrowych
        emp_fields = [
            "pesel",
            "nr_konta",
            "adres_zamieszkania",
            "stawka_godzinowa",
            "data_zatrudnienia",
        ]
        has_emp_fields = any(f in data for f in emp_fields)

        if has_emp_fields:
            if g.current_role != "administrator":
                pass

            date_zatr = None
            if data.get("data_zatrudnienia"):
                try:
                    date_zatr = datetime.strptime(
                        data["data_zatrudnienia"], "%Y-%m-%d"
                    ).date()
                except ValueError:
                    pass

            if user.dane_kadrowe:
                EmployeeService.update_employee_data(
                    session,
                    user_id,
                    pesel=data.get("pesel"),
                    nr_konta=data.get("nr_konta"),
                    adres_zamieszkania=data.get("adres_zamieszkania"),
                    stawka_godzinowa=data.get("stawka_godzinowa"),
                    data_zatrudnienia=date_zatr,
                )
            else:
                if data.get("pesel"):
                    try:
                        EmployeeService.create_employee_data(
                            session,
                            user_id,
                            pesel=data["pesel"],
                            nr_konta=data.get("nr_konta"),
                            adres_zamieszkania=data.get("adres_zamieszkania"),
                            stawka_godzinowa=data.get("stawka_godzinowa"),
                            data_zatrudnienia=date_zatr,
                        )
                    except ValueError as e:
                        # Abort, aby wymusic rollback transakcji w przypadku bledu (np. duplikat PESEL)
                        abort(400, description=str(e))

        return "", 204
