from flask import Blueprint, request, jsonify
from backend.services.parts_order_service import PartsOrderService

parts_orders_bp = Blueprint("parts_orders", __name__)


@parts_orders_bp.route("/parts-orders", methods=["POST"])
def create_parts_order():
    payload = request.json or {}
    skladajacy_id = payload.get("id_skladajacego")

    if not skladajacy_id:
        return jsonify({"error": "id_skladajacego required"}), 400

    try:
        order_id = PartsOrderService.create_order(int(skladajacy_id))
        return jsonify({"id_zamowienia": order_id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@parts_orders_bp.route("/parts-orders/<int:order_id>/items", methods=["POST"])
def add_order_item(order_id: int):
    payload = request.json or {}
    part_id = payload.get("id_czesci")
    ilosc = payload.get("ilosc")
    cena = payload.get("cena_jednostkowa")

    if not part_id or ilosc is None or cena is None:
        return jsonify({"error": "id_czesci, ilosc, cena_jednostkowa required"}), 400

    try:
        item_id = PartsOrderService.add_item(
            order_id, int(part_id), int(ilosc), float(cena)
        )
        return jsonify({"id_pozycji": item_id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@parts_orders_bp.route("/parts-orders/<int:order_id>/status", methods=["POST"])
def change_order_status(order_id: int):
    payload = request.json or {}
    status_name = payload.get("status_name")
    zatwierdzajacy_id = payload.get("zatwierdzajacy_id")

    if not status_name:
        return jsonify({"error": "status_name required"}), 400

    try:
        result = PartsOrderService.change_status(
            order_id, status_name, zatwierdzajacy_id
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@parts_orders_bp.route("/parts-orders", methods=["GET"])
def list_parts_orders():
    return jsonify(PartsOrderService.list_orders())
