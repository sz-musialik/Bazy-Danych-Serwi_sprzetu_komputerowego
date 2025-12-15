from flask import Blueprint, request, jsonify
from backend.services.parts_service import PartsService

parts_bp = Blueprint("parts", __name__)


@parts_bp.route("/parts", methods=["POST"])
def create_part():
    payload = request.json or {}

    if "nazwa_czesci" not in payload:
        return jsonify({"error": "nazwa_czesci required"}), 400

    try:
        part_id = PartsService.add_part(
            nazwa_czesci=payload["nazwa_czesci"],
            typ_czesci=payload.get("typ_czesci"),
            producent=payload.get("producent"),
            numer_katalogowy=payload.get("numer_katalogowy"),
            cena_katalogowa=float(payload["cena_katalogowa"])
            if payload.get("cena_katalogowa") is not None
            else None,
            ilosc_dostepna=int(payload.get("ilosc_dostepna", 0)),
        )
        return jsonify({"id_czesci": part_id}), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "failed to create part", "details": str(e)}), 500


@parts_bp.route("/parts", methods=["GET"])
def list_parts():
    return jsonify(PartsService.list_parts())


@parts_bp.route("/parts/<int:part_id>", methods=["PUT"])
def update_part(part_id: int):
    payload = request.json or {}

    try:
        PartsService.update_part(
            part_id,
            nazwa_czesci=payload.get("nazwa_czesci"),
            producent=payload.get("producent"),
            numer_katalogowy=payload.get("numer_katalogowy"),
            cena_katalogowa=payload.get("cena_katalogowa"),
            ilosc_dostepna=payload.get("ilosc_dostepna"),
        )
        return "", 204

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "failed to update part", "details": str(e)}), 500


@parts_bp.route("/parts/<int:part_id>/stock", methods=["POST"])
def change_stock(part_id: int):
    payload = request.json or {}
    delta = payload.get("ilosc_zmiana")

    if delta is None:
        return jsonify({"error": "ilosc_zmiana required"}), 400

    try:
        PartsService.update_stock(part_id, int(delta))
        return "", 204

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "failed to update stock", "details": str(e)}), 500
