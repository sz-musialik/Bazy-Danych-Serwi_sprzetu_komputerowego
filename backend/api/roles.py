from flask import Blueprint, jsonify
from backend.db.session import transactional_session
from backend.models.role import Role
from backend.auth.security import require_role

roles_bp = Blueprint("roles", __name__)


@roles_bp.route("/roles", methods=["GET"])
@require_role("administrator", "manager")
def list_roles():
    with transactional_session() as db:
        roles = db.query(Role).order_by(Role.id_rola.asc()).all()
        return jsonify(
            [{"id_rola": r.id_rola, "nazwa_rola": r.nazwa_rola} for r in roles]
        )
