from flask import Blueprint, request, jsonify
from backend.services.client_service import ClientService
from backend.db.session import transactional_session
from backend.models.client import Client

clients_bp = Blueprint("clients", __name__)

@clients_bp.route("/clients", methods=["POST"])
def create_client():
    data = request.json or {}

    client_id = ClientService.create_client(
        nazwa=data.get("nazwa"),
        adres=data.get("adres"),
        email=data.get("email"),
        telefon=data.get("telefon"),
    )

    return jsonify({"id_klienta": client_id}), 201


@clients_bp.route("/clients", methods=["GET"])
def get_clients():
    with transactional_session() as session:
        clients = session.query(Client)\
            .filter(Client.czy_aktywny == True)\
            .all()

        return jsonify([
            {
                "id_klienta": c.id_klienta,
                "imie": c.imie,
                "email": c.email
            }
            for c in clients
        ])


@clients_bp.route("/clients/<int:client_id>", methods=["DELETE"])
def soft_delete_client(client_id):
    with transactional_session() as session:
        client = session.get(Client, client_id)

        if not client:
            return jsonify({"error": "Client not found"}), 404

        client.czy_aktywny = False
        session.add(client)

        return jsonify({
            "message": "Client deactivated",
            "id_klienta": client.id_klienta
        })