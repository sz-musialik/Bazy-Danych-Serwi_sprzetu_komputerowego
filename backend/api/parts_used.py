from flask import Blueprint, request, jsonify
from backend.services.parts_used_service import PartsUsedService

parts_used_bp = Blueprint("parts_used", __name__)

@parts_used_bp.route('/orders/<int:order_id>/parts', methods=['POST'])
def add_used_part(order_id: int):
    payload = request.json or {}
    part_id = payload.get('part_id') or payload.get('id_czesci')
    quantity = payload.get('quantity') or payload.get('ilosc')
    unit_price = payload.get('unit_price') or payload.get('cena_jednostkowa')

    if not part_id or quantity is None or unit_price is None:
        return jsonify({'error': 'part_id, quantity and unit_price are required'}), 400

    try:
        used = PartsUsedService.add_used_part(order_id, int(part_id), int(quantity), float(unit_price))
        return jsonify({'id_pozycji': used.id_pozycji, 'id_zlecenia': used.id_zlecenia}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'failed to add used part', 'details': str(e)}), 500

@parts_used_bp.route('/orders/<int:order_id>/parts', methods=['GET'])
def list_used_parts(order_id: int):
    parts = PartsUsedService.list_used_parts(order_id)
    return jsonify([
        {
            'id_pozycji': p.id_pozycji,
            'id_czesci': p.id_czesci,
            'ilosc': p.ilosc,
            'cena_jednostkowa': float(p.cena_jednostkowa)
        }
        for p in parts
    ])

