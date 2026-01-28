from flask import Blueprint, request, jsonify, g
from backend.db.session import transactional_session
from backend.models.order import Order
from backend.models.client import Client
from backend.models.user import User
from backend.auth.security import require_role
from datetime import date, datetime

orders_bp = Blueprint("orders", __name__)


def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def handle_status_change_logic(order, new_status_id):
    """
    Automatycznie zarzadzanie data zakonczenia w zalezności od statusu.
    ID 5 = Zakonczone, ID 6 = Zarchiwizowane.
    """
    prev_status = order.status_zlecenia
    order.status_zlecenia = new_status_id

    # Jesli zmieniamy na status "aktywny" (czyli NIE zakonczone i NIE zarchiwizowane)
    if new_status_id not in [5, 6]:
        # Kasujemy date zakonczenia, bo zlecenie znowu jest w toku
        order.data_zakonczenia = None

    # Jesli zmieniamy na Zakonczone, a data jest pusta -> ustawiamy dzisiaj
    elif new_status_id == 5 and order.data_zakonczenia is None:
        order.data_zakonczenia = datetime.now().date()


@orders_bp.route("/orders/<int:order_id>/status", methods=["PATCH"])
@require_role("administrator", "manager", "pracownik")
def update_order_status(order_id: int):
    payload = request.json or {}
    new_status = payload.get("status_zlecenia")

    with transactional_session() as session:
        order = session.query(Order).filter(Order.id_zlecenia == order_id).first()
        if not order:
            return jsonify({"error": "order not found"}), 404

        if (
            g.current_role == "pracownik"
            and order.id_pracownika != g.current_user.id_uzytkownika
        ):
            return jsonify({"error": "forbidden"}), 403

        if new_status:
            handle_status_change_logic(order, int(new_status))

        return "", 204


# Tworzenie Zlecenia
@orders_bp.route("/orders", methods=["POST"])
@require_role("administrator", "manager", "pracownik")
def create_order():
    data = request.json or {}

    requested_worker_id = data.get("id_pracownika")
    if g.current_role == "pracownik":
        worker_id = g.current_user.id_uzytkownika
    else:
        # Jesli kierownik/admin nie wybral, przypisz do niego
        worker_id = (
            int(requested_worker_id)
            if requested_worker_id
            else g.current_user.id_uzytkownika
        )

    with transactional_session() as session:
        order = Order(
            id_klienta=int(data["id_klienta"]),
            id_pracownika=worker_id,
            typ_sprzetu=int(data["id_typu_sprzetu"]),
            opis_usterki=data.get("opis_usterki"),
            status_zlecenia=1,
            marka_sprzetu=data.get("marka"),
            model_sprzetu=data.get("model"),
            numer_seryjny=data.get("sn"),
        )
        session.add(order)
        session.flush()
        return jsonify({"id_zlecenia": order.id_zlecenia}), 201


# Pobieranie Listy
@orders_bp.route("/orders", methods=["GET"])
@require_role("administrator", "manager", "pracownik")
def get_orders():
    with transactional_session() as session:
        # Laczenie z Client (inner join) oraz User
        q = (
            session.query(Order, Client, User)
            .join(Client, Order.id_klienta == Client.id_klienta)
            .outerjoin(User, Order.id_pracownika == User.id_uzytkownika)
        )

        if g.current_role == "pracownik":
            q = q.filter(Order.id_pracownika == g.current_user.id_uzytkownika)
            q = q.filter(Order.status_zlecenia != 5)  # Ukryj zakonczone
            q = q.filter(Order.status_zlecenia != 6)  # Ukryj zarchiwizowane

        results = q.order_by(Order.id_zlecenia.desc()).all()

        output = []
        for o, c, u in results:
            worker_name = f"{u.imie} {u.nazwisko}" if u else "Nieznany"

            output.append(
                {
                    "id_zlecenia": o.id_zlecenia,
                    "typ_sprzetu": o.typ_sprzetu,
                    "status_zlecenia": o.status_zlecenia,
                    "opis_usterki": o.opis_usterki,
                    "id_pracownika": o.id_pracownika,
                    "pracownik_imie_nazwisko": worker_name,
                    "klient_imie_nazwisko": f"{c.imie} {c.nazwisko}",
                    "data_rozpoczecia": (
                        str(o.data_rozpoczecia) if o.data_rozpoczecia else None
                    ),
                    "data_zakonczenia": (
                        str(o.data_zakonczenia) if o.data_zakonczenia else None
                    ),
                    "koszt_robocizny": (
                        str(o.koszt_robocizny) if o.koszt_robocizny else "0.00"
                    ),
                    "koszt_czesci": str(o.koszt_czesci) if o.koszt_czesci else "0.00",
                    "marka_sprzetu": o.marka_sprzetu,
                    "model_sprzetu": o.model_sprzetu,
                    "numer_seryjny": o.numer_seryjny,
                    "diagnoza": o.diagnoza,
                    "wykonane_czynnosci": o.wykonane_czynnosci,
                }
            )
        return jsonify(output)


@orders_bp.route("/orders/<int:order_id>", methods=["PUT"])
@require_role("administrator", "manager", "pracownik")
def update_order_details(order_id: int):
    data = request.json or {}

    with transactional_session() as session:
        order = session.query(Order).filter(Order.id_zlecenia == order_id).first()
        if not order:
            return jsonify({"error": "Not found"}), 404

        if g.current_role == "pracownik":
            if order.id_pracownika != g.current_user.id_uzytkownika:
                return jsonify({"error": "Forbidden"}), 403

            # Pracownik (pola edytowalne)
            order.opis_usterki = data.get("opis_usterki", order.opis_usterki)
            order.marka_sprzetu = data.get("marka_sprzetu", order.marka_sprzetu)
            order.model_sprzetu = data.get("model_sprzetu", order.model_sprzetu)
            order.numer_seryjny = data.get("numer_seryjny", order.numer_seryjny)
            order.diagnoza = data.get("diagnoza", order.diagnoza)
            order.wykonane_czynnosci = data.get(
                "wykonane_czynnosci", order.wykonane_czynnosci
            )
            order.koszt_robocizny = data.get("koszt_robocizny", order.koszt_robocizny)

            # Pracownik zmienia status -> uruchomienie logiki dat
            if "status_zlecenia" in data:
                handle_status_change_logic(order, int(data["status_zlecenia"]))

        else:
            # Administrator/Kierownik
            # Najpierw aktualizujemy status (bo on moze zresetowac date)
            if "status_zlecenia" in data:
                handle_status_change_logic(order, int(data["status_zlecenia"]))

            # Potem ewentualnie reczna edycja daty przez Administratora
            # Jesli w JSON przyszla data_zakonczenia, to ja ustawiamy
            if "data_zakonczenia" in data:
                # Jesli null w JSON -> ustaw null
                if data["data_zakonczenia"] is None:
                    order.data_zakonczenia = None
                else:
                    order.data_zakonczenia = parse_date(data["data_zakonczenia"])

            if "data_rozpoczecia" in data:
                order.data_rozpoczecia = parse_date(data["data_rozpoczecia"])
            if "koszt_czesci" in data:
                order.koszt_czesci = data["koszt_czesci"]
            if "id_pracownika" in data:
                order.id_pracownika = int(data["id_pracownika"])

            order.opis_usterki = data.get("opis_usterki", order.opis_usterki)
            order.marka_sprzetu = data.get("marka_sprzetu", order.marka_sprzetu)
            order.model_sprzetu = data.get("model_sprzetu", order.model_sprzetu)
            order.numer_seryjny = data.get("numer_seryjny", order.numer_seryjny)
            order.diagnoza = data.get("diagnoza", order.diagnoza)
            order.wykonane_czynnosci = data.get(
                "wykonane_czynnosci", order.wykonane_czynnosci
            )
            order.koszt_robocizny = data.get("koszt_robocizny", order.koszt_robocizny)

        return "", 204
