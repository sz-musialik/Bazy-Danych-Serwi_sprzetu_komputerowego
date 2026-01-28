from flask import Blueprint, request, jsonify
from backend.db.session import transactional_session
from backend.models.parts import Part
from backend.auth.security import require_role

parts_bp = Blueprint("parts", __name__)


# Pobieranie Listy Czesci
# Wszyscy moga widziec stan magazynu
@parts_bp.route("/parts", methods=["GET"])
@require_role("administrator", "manager", "pracownik")
def get_parts():
    with transactional_session() as session:
        parts = session.query(Part).order_by(Part.id_czesci).all()
        return jsonify(
            [
                {
                    "id_czesci": p.id_czesci,
                    "nazwa_czesci": p.nazwa_czesci,
                    "typ_czesci": p.typ_czesci,
                    "producent": p.producent,
                    "ilosc_dostepna": p.ilosc_dostepna,
                    "numer_katalogowy": p.numer_katalogowy,
                    "cena_katalogowa": (
                        str(p.cena_katalogowa) if p.cena_katalogowa else "0.00"
                    ),
                }
                for p in parts
            ]
        )


# Dodawanie Czesci
@parts_bp.route("/parts", methods=["POST"])
@require_role("administrator")
def create_part():
    data = request.json or {}
    if not data.get("nazwa_czesci") or not data.get("typ_czesci"):
        return jsonify({"error": "Nazwa i typ części są wymagane"}), 400

    with transactional_session() as session:
        part = Part(
            nazwa_czesci=data["nazwa_czesci"],
            typ_czesci=data["typ_czesci"],
            producent=data.get("producent", ""),
            ilosc_dostepna=int(data.get("ilosc_dostepna", 0)),
            numer_katalogowy=data.get("numer_katalogowy", ""),
            cena_katalogowa=data.get("cena_katalogowa", 0.00),
        )
        session.add(part)
        session.flush()
        return jsonify({"id_czesci": part.id_czesci}), 201


# Edycja Czesci
@parts_bp.route("/parts/<int:part_id>", methods=["PUT"])
@require_role("administrator")
def update_part(part_id: int):
    data = request.json or {}
    with transactional_session() as session:
        part = session.query(Part).filter(Part.id_czesci == part_id).first()
        if not part:
            return jsonify({"error": "Part not found"}), 404

        part.nazwa_czesci = data.get("nazwa_czesci", part.nazwa_czesci)
        part.typ_czesci = data.get("typ_czesci", part.typ_czesci)
        part.producent = data.get("producent", part.producent)
        part.numer_katalogowy = data.get("numer_katalogowy", part.numer_katalogowy)

        if "ilosc_dostepna" in data:
            part.ilosc_dostepna = int(data["ilosc_dostepna"])

        if "cena_katalogowa" in data:
            part.cena_katalogowa = data["cena_katalogowa"]

        return "", 204
