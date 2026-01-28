from flask import Blueprint, request, jsonify, g
from backend.services.client_service import ClientService
from backend.db.session import transactional_session
from backend.models.client import Client
from backend.models.order import Order
from backend.auth.security import require_role

clients_bp = Blueprint("clients", __name__)


@clients_bp.route("/clients", methods=["POST"])
@require_role("administrator", "manager", "pracownik")
def create_client():
    payload = request.json or {}

    try:
        client_id = ClientService.create_client(
            imie=payload.get("imie"),
            nazwisko=payload.get("nazwisko"),
            email=payload.get("email"),
            nr_telefonu=payload.get("nr_telefonu"),
            adres=payload.get("adres"),
        )
        return jsonify({"id_klienta": client_id}), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@clients_bp.route("/clients", methods=["GET"])
@require_role("administrator", "manager", "pracownik")
def get_clients():
    scope = request.args.get("scope", "all")  # Domyslnie "all"

    with transactional_session() as session:
        # Pracownik ma widziec TYLKO swoich aktywnych klientow
        if g.current_role == "pracownik" and scope == "active_orders":
            clients = (
                session.query(Client)
                .join(Order, Order.id_klienta == Client.id_klienta)
                .filter(Order.id_pracownika == g.current_user.id_uzytkownika)
                .filter(Order.status_zlecenia != 5)  # Tylko niezakonczone
                .distinct()
                .all()
            )
        else:
            # Wyszukiwarka (pracownik) LUB Admin/Kierownik (wszedzie)
            # Zwracamy wszystkich klientów
            clients = session.query(Client).order_by(Client.id_klienta).all()

        return jsonify(
            [
                {
                    "id_klienta": c.id_klienta,
                    "imie": c.imie,
                    "nazwisko": c.nazwisko,
                    "email": c.email,
                    "nr_telefonu": c.nr_telefonu,
                    "adres": c.adres,
                }
                for c in clients
            ]
        )


@clients_bp.route("/clients/<int:client_id>", methods=["PUT"])
@require_role("administrator")
def update_client(client_id: int):
    payload = request.json or {}
    try:
        ClientService.update_client(
            client_id,
            imie=payload.get("imie"),
            nazwisko=payload.get("nazwisko"),
            email=payload.get("email"),
            nr_telefonu=payload.get("nr_telefonu"),
            adres=payload.get("adres"),
        )
        return "", 204
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
