from __future__ import annotations

import os
from functools import wraps
from typing import Callable, Optional, Any

from flask import request, jsonify, current_app, g
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from backend.db.session import transactional_session
from backend.models.user import User

AUTH_DISABLED = os.getenv("DISABLE_AUTH", "0") in ("1", "true", "True")


def _serializer() -> URLSafeTimedSerializer:
    secret = current_app.config.get("SECRET_KEY")
    if not secret:
        raise RuntimeError("SECRET_KEY is not set on Flask app")
    return URLSafeTimedSerializer(secret, salt="auth-token")


def issue_token(user_id: int) -> str:
    return _serializer().dumps({"uid": user_id})


def verify_token(token: str, max_age_seconds: int = 60 * 60 * 8) -> Optional[int]:
    try:
        data = _serializer().loads(token, max_age=max_age_seconds)
        return int(data["uid"])
    except (BadSignature, SignatureExpired, KeyError, TypeError, ValueError):
        return None


def get_current_user() -> Optional[User]:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None

    token = auth.removeprefix("Bearer ").strip()
    uid = verify_token(token)
    if not uid:
        return None

    with transactional_session() as db:
        user = db.query(User).filter(User.id_uzytkownika == uid).first()
        if not user or not user.czy_aktywny:
            return None

        db.expunge(user)
        return user


def _dev_user() -> User:
    """
    Uzytkownik "na sztywno" dla DISABLE_AUTH=1.
    """
    u = User(
        id_uzytkownika=1,
        imie="DEV",
        nazwisko="USER",
        login="dev",
        haslo_hash="",
        czy_aktywny=True,
    )
    return u


def require_auth(fn: Callable[..., Any]):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if AUTH_DISABLED:
            g.current_user = _dev_user()
            g.current_role = "admin"
            return fn(*args, **kwargs)

        user = get_current_user()
        if not user:
            return jsonify({"error": "unauthorized"}), 401

        g.current_user = user
        return fn(*args, **kwargs)

    return wrapper


def require_role(*allowed_roles: str):
    def decorator(fn: Callable[..., Any]):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if AUTH_DISABLED:
                g.current_user = _dev_user()
                g.current_role = "admin"
                return fn(*args, **kwargs)

            user = get_current_user()
            if not user:
                return jsonify({"error": "unauthorized"}), 401

            with transactional_session() as db:
                u = (
                    db.query(User)
                    .filter(User.id_uzytkownika == user.id_uzytkownika)
                    .first()
                )
                if not u or not u.czy_aktywny:
                    return jsonify({"error": "unauthorized"}), 401

                role_name = u.role.nazwa_rola if u.role else None

            if role_name not in allowed_roles:
                return jsonify({"error": "forbidden"}), 403

            g.current_user = user
            g.current_role = role_name
            return fn(*args, **kwargs)

        return wrapper

    return decorator
