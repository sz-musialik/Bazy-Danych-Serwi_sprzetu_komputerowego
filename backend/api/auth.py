from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash

from backend.db.session import transactional_session
from backend.models.user import User
from backend.auth.security import issue_token, require_auth
from flask import g

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    payload = request.json or {}
    login = payload.get("login")
    password = payload.get("password")

    if not login or not password:
        return jsonify({"error": "login and password required"}), 400

    with transactional_session() as db:
        user = db.query(User).filter(User.login == login).first()

        if not user or not user.czy_aktywny:
            return jsonify({"error": "invalid credentials"}), 401

        if not check_password_hash(user.haslo_hash, password):
            return jsonify({"error": "invalid credentials"}), 401

        token = issue_token(user.id_uzytkownika)
        return jsonify({
            "token": token,
            "user": {
                "id_uzytkownika": user.id_uzytkownika,
                "imie": user.imie,
                "nazwisko": user.nazwisko,
                "login": user.login,
                "rola": user.role.nazwa_rola if user.role else None,
            }
        })


@auth_bp.route("/auth/me", methods=["GET"])
@require_auth
def me():
    u = g.current_user
    return jsonify({
        "id_uzytkownika": u.id_uzytkownika,
        "imie": u.imie,
        "nazwisko": u.nazwisko,
        "login": u.login,
    })
