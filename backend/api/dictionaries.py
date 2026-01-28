from flask import Blueprint, jsonify
from backend.db.session import transactional_session
from backend.models.equipment_type import EquipmentType
from backend.models.order_status import OrderStatus
from backend.models.part_type import PartType

dictionaries_bp = Blueprint("dictionaries", __name__)


@dictionaries_bp.route("/dictionaries/equipment-types", methods=["GET"])
def get_equipment_types():
    with transactional_session() as session:
        types = session.query(EquipmentType).all()
        # Mapa: "Nazwa sprzetu": ID
        return jsonify({t.nazwa_typu: t.id_typu for t in types})


@dictionaries_bp.route("/dictionaries/statuses", methods=["GET"])
def get_statuses():
    with transactional_session() as session:
        statuses = session.query(OrderStatus).all()
        # Mapa: "Nazwa Statusu": ID
        return jsonify({s.nazwa_statusu: s.id_statusu for s in statuses})


@dictionaries_bp.route("/dictionaries/part-types", methods=["GET"])
def get_part_types():
    with transactional_session() as session:
        types = session.query(PartType).all()
        # Mapa: "Nazwa czesci": ID
        return jsonify({t.nazwa_typu: t.id_typu for t in types})
