from flask import Blueprint, request, jsonify
from backend.services.order_service import OrderService
from backend.db.session import transactional_session
from backend.models.order import Order
orders_bp = Blueprint("orders", __name__)

@orders_bp.route("/orders", methods=["POST"])
def create_order():
    data = request.json or {}

    try:
        order_id = OrderService().create_order(
            actor_user=type(
                "User", (), {
                    "id_uzytkownika": data.get("id_pracownika"),
                    "is_admin": True,
                    "is_manager": True
                }
            )(),
            client_id=data.get("id_klienta"),
            equipment_type_id=data.get("id_typu_sprzetu"),
            description=data.get("opis")
        )
        return jsonify({"id_zlecenia": order_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@orders_bp.route("/orders", methods=["GET"])
def get_orders():
    with transactional_session() as session:
        orders = session.query(Order).all()

        return jsonify([
            {
                "id_zlecenia": o.id_zlecenia,
                "id_klienta": o.id_klienta,
                "id_pracownika": o.id_pracownika,
                "status_zlecenia": o.status_zlecenia,
                "opis_usterki": o.opis_usterki
            }
            for o in orders
        ])