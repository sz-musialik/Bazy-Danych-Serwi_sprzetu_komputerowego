from flask import Blueprint, request, jsonify
from backend.services.client_service import ClientService
from backend.db.session import transactional_session
from backend.models.client import Client

clients_bp = Blueprint("clients", __name__)


@clients_bp.route("/clients", methods=["POST"])
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
def get_clients():
    return jsonify(ClientService.get_all_clients())

