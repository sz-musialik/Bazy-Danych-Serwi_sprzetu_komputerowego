from flask import Blueprint, request, jsonify
from backend.services.parts_order_service import PartsOrderService

parts_orders_bp = Blueprint("parts_orders", __name__)


@parts_orders_bp.route("/parts-orders", methods=["POST"])
def create_parts_order():
    payload = request.json or {}
    if not payload.get("id_skladajacego"):
        return jsonify({"error": "id_skladajacego required"}), 400
    if not payload.get("nazwa_czesci"):
        return jsonify({"error": "nazwa_czesci required"}), 400

    try:
        order_id = PartsOrderService.submit_order(payload)
        return (
            jsonify(
                {"id_zamowienia": order_id, "message": "Zamówienie zostało złożone"}
            ),
            201,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Wystąpił błąd serwera", "details": str(e)}), 500


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


@parts_orders_bp.route("/parts-orders/<int:order_id>", methods=["GET"])
def get_parts_order(order_id: int):
    try:
        return jsonify(PartsOrderService.get_order_details(order_id)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


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


@parts_orders_bp.route("/parts-orders/<int:order_id>/approve", methods=["POST"])
def approve_parts_order(order_id: int):
    payload = request.json or {}
    zatwierdzajacy_id = payload.get("zatwierdzajacy_id")
    if not zatwierdzajacy_id:
        return jsonify({"error": "zatwierdzajacy_id required"}), 400
    try:
        return jsonify(PartsOrderService.approve(order_id, int(zatwierdzajacy_id))), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@parts_orders_bp.route("/parts-orders/<int:order_id>/reject", methods=["POST"])
def reject_parts_order(order_id: int):
    payload = request.json or {}
    zatwierdzajacy_id = payload.get("zatwierdzajacy_id")
    if not zatwierdzajacy_id:
        return jsonify({"error": "zatwierdzajacy_id required"}), 400
    try:
        return jsonify(PartsOrderService.reject(order_id, int(zatwierdzajacy_id))), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@parts_orders_bp.route("/parts-orders/<int:order_id>/receive", methods=["POST"])
def receive_parts_order(order_id: int):
    try:
        return jsonify(PartsOrderService.receive(order_id)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@parts_orders_bp.route(
    "/parts-orders/<int:order_id>/items/<int:item_id>", methods=["DELETE"]
)
def delete_parts_order_item(order_id: int, item_id: int):
    try:
        PartsOrderService.delete_item(order_id, item_id)
        return "", 204
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "failed to delete item", "details": str(e)}), 500


@parts_orders_bp.route("/parts-orders/<int:order_id>", methods=["DELETE"])
def delete_parts_order(order_id: int):
    try:
        PartsOrderService.delete_order(order_id)
        return "", 204
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return (
            jsonify({"error": "failed to delete parts order", "details": str(e)}),
            500,
        )


@parts_orders_bp.route("/parts-orders", methods=["GET"])
def list_parts_orders():
    user_id_arg = request.args.get("user_id")
    user_id = int(user_id_arg) if user_id_arg else None

    return jsonify(PartsOrderService.list_orders(filter_user_id=user_id))
