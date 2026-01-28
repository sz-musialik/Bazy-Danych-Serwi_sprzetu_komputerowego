from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

from flask import Blueprint, request, jsonify
from sqlalchemy import func

from backend.db.session import transactional_session
from backend.models.order import Order
from backend.models.parts_used import PartsUsed
from backend.models.parts import Part

reports_bp = Blueprint("reports", __name__)


def _parse_yyyy_mm_dd(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d")


@reports_bp.route("/reports/summary", methods=["GET"])
def summary():
    date_from = request.args.get("from")  # YYYY-MM-DD
    date_to = request.args.get("to")  # YYYY-MM-DD

    try:
        dt_from = _parse_yyyy_mm_dd(date_from) if date_from else None
        dt_to_exclusive = (
            (_parse_yyyy_mm_dd(date_to) + timedelta(days=1)) if date_to else None
        )
    except ValueError:
        return jsonify({"error": "Bad date format. Use YYYY-MM-DD for from/to"}), 400

    with transactional_session() as session:
        q = session.query(Order)
        if dt_from:
            q = q.filter(Order.data_rozpoczecia >= dt_from)
        if dt_to_exclusive:
            q = q.filter(Order.data_rozpoczecia < dt_to_exclusive)

        orders = q.all()
        order_ids = [o.id_zlecenia for o in orders]

        # Koszty robocizny
        total_labor = Decimal("0.00")
        for o in orders:
            total_labor += o.koszt_robocizny or Decimal("0.00")

        # Koszty czesci liczone z czesci_wykorzystane (ilosc * cena_jednostkowa)
        total_parts = Decimal("0.00")
        if order_ids:
            parts_sum = (
                session.query(func.sum(PartsUsed.ilosc * PartsUsed.cena_jednostkowa))
                .filter(PartsUsed.id_zlecenia.in_(order_ids))
                .scalar()
            )
            if parts_sum is not None:
                total_parts = Decimal(str(parts_sum))

        # Statusy
        status_q = session.query(Order.status_zlecenia, func.count(Order.id_zlecenia))
        if dt_from:
            status_q = status_q.filter(Order.data_rozpoczecia >= dt_from)
        if dt_to_exclusive:
            status_q = status_q.filter(Order.data_rozpoczecia < dt_to_exclusive)

        status_rows = status_q.group_by(Order.status_zlecenia).all()

        top_q = session.query(
            PartsUsed.id_czesci, func.sum(PartsUsed.ilosc).label("qty")
        )
        if order_ids:
            top_q = top_q.filter(PartsUsed.id_zlecenia.in_(order_ids))
        else:
            top_q = top_q.filter(False)

        top_rows = (
            top_q.group_by(PartsUsed.id_czesci)
            .order_by(func.sum(PartsUsed.ilosc).desc())
            .limit(5)
            .all()
        )

        top_parts = []
        for part_id, qty in top_rows:
            part = session.query(Part).filter(Part.id_czesci == int(part_id)).first()
            top_parts.append(
                {
                    "id_czesci": int(part_id),
                    "nazwa_czesci": part.nazwa_czesci if part else None,
                    "ilosc_lacznie": int(qty or 0),
                }
            )

        return jsonify(
            {
                "zakres": {"from": date_from, "to": date_to},
                "zlecenia": {
                    "liczba": len(orders),
                    "statusy": [
                        {"status_zlecenia": int(s), "liczba": int(c)}
                        for s, c in status_rows
                    ],
                },
                "koszty": {
                    "koszt_robocizny": float(total_labor),
                    "koszt_czesci": float(total_parts),
                    "razem": float(total_labor + total_parts),
                },
                "top_czesci": top_parts,
            }
        )
