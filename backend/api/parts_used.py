from __future__ import annotations
from flask import Blueprint, request, jsonify
from backend.services.parts_used_service import PartsUsedService


parts_used_bp = Blueprint("parts_used", __name__)


@parts_used_bp.route("/orders/<int:order_id>/parts-used", methods=["POST"])
def add_used_part(order_id: int):
    payload = request.json or {}

    part_id = payload.get("part_id", payload.get("id_czesci"))
    quantity = payload.get("quantity", payload.get("ilosc"))
    unit_price = payload.get("unit_price", payload.get("cena_jednostkowa"))

    if part_id is None or quantity is None or unit_price is None:
        return (
            jsonify(
                {
                    "error": "part_id/id_czesci, quantity/ilosc i unit_price/cena_jednostkowa są wymagane"
                }
            ),
            400,
        )

    try:
        used = PartsUsedService.add_used_part(
            order_id=order_id,
            part_id=int(part_id),
            quantity=int(quantity),
            unit_price=float(unit_price),
        )

        return (
            jsonify(
                {
                    "id_pozycji": used.id_pozycji,
                    "id_zlecenia": used.id_zlecenia,
                    "id_czesci": used.id_czesci,
                    "ilosc": used.ilosc,
                    "cena_jednostkowa": float(used.cena_jednostkowa),
                    "data_wykorzystania": (
                        used.data_wykorzystania.isoformat()
                        if used.data_wykorzystania
                        else None
                    ),
                }
            ),
            201,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "failed to add used part", "details": str(e)}), 500


@parts_used_bp.route("/orders/<int:order_id>/parts-used", methods=["GET"])
def list_used_parts(order_id: int):
    try:
        parts = PartsUsedService.list_used_parts(order_id)
        return jsonify(
            [
                {
                    "id_pozycji": p.id_pozycji,
                    "id_zlecenia": p.id_zlecenia,
                    "id_czesci": p.id_czesci,
                    "ilosc": p.ilosc,
                    "cena_jednostkowa": float(p.cena_jednostkowa),
                    "data_wykorzystania": (
                        p.data_wykorzystania.isoformat()
                        if p.data_wykorzystania
                        else None
                    ),
                }
                for p in parts
            ]
        )
    except Exception as e:
        return jsonify({"error": "failed to list used parts", "details": str(e)}), 500


@parts_used_bp.route(
    "/orders/<int:order_id>/parts-used/<int:used_part_id>",
    methods=["PUT"],
)
def update_used_part(order_id: int, used_part_id: int):
    payload = request.json or {}
    new_quantity = payload.get("ilosc")

    if new_quantity is None:
        return jsonify({"error": "ilosc jest wymagana"}), 400

    try:
        PartsUsedService.update_used_part_quantity(
            order_id=order_id,
            used_part_id=used_part_id,
            new_quantity=int(new_quantity),
        )
        return jsonify({"status": "updated"}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "failed to update used part", "details": str(e)}), 500


@parts_used_bp.route(
    "/orders/<int:order_id>/parts-used/<int:used_part_id>",
    methods=["DELETE"],
)
def delete_used_part(order_id: int, used_part_id: int):
    try:
        PartsUsedService.delete_used_part(order_id=order_id, used_part_id=used_part_id)
        return "", 204
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "failed to delete used part", "details": str(e)}), 500
