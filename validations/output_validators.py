from datetime import datetime
from typing import Any


def validate_part(part: Any) -> None:
    if part is None:
        raise ValueError("Part is None")
    if not hasattr(part, 'id_czesci'):
        raise ValueError("Part missing id_czesci")
    if not hasattr(part, 'nazwa_czesci') or not part.nazwa_czesci:
        raise ValueError("Part must have a name")
    if hasattr(part, 'ilosc_dostepna') and part.ilosc_dostepna is not None:
        if not isinstance(part.ilosc_dostepna, int) or part.ilosc_dostepna < 0:
            raise ValueError("ilosc_dostepna must be non-negative int")


def validate_client(client: Any) -> None:
    if client is None:
        raise ValueError("Client is None")
    if not hasattr(client, 'id_klienta'):
        raise ValueError("Client missing id_klienta")
    if not (hasattr(client, 'imie') or hasattr(client, 'nazwisko')):
        raise ValueError("Client must have name")


def validate_order(order: Any) -> None:
    if order is None:
        raise ValueError("Order is None")
    if not hasattr(order, 'id_zlecenia'):
        raise ValueError("Order missing id_zlecenia")
    if not hasattr(order, 'id_klienta'):
        raise ValueError("Order must reference client")
    if not hasattr(order, 'data_rozpoczecia'):
        raise ValueError("Order must have creation date")
    if getattr(order, 'data_rozpoczecia') and not isinstance(order.data_rozpoczecia, datetime):
        raise ValueError("data_rozpoczecia must be datetime")


def validate_used_part(used_part: Any) -> None:
    if used_part is None:
        raise ValueError("UsedPart is None")
    if not hasattr(used_part, 'id_pozycji'):
        raise ValueError("UsedPart missing id_pozycji")
    if not hasattr(used_part, 'ilosc') or used_part.ilosc <= 0:
        raise ValueError("UsedPart ilosc must be positive")


def validate_part_order(part_order: Any) -> None:
    if part_order is None:
        raise ValueError("PartOrder is None")
    if not hasattr(part_order, 'id_zamowienia'):
        raise ValueError("PartOrder missing id_zamowienia")
    if not hasattr(part_order, 'status_zamowienia'):
        raise ValueError("PartOrder missing status_zamowienia")


def validate_user(user: Any) -> None:
    if user is None:
        raise ValueError("User is None")
    if not hasattr(user, 'id_uzytkownika'):
        raise ValueError("User missing id_uzytkownika")
    if not hasattr(user, 'login') or not user.login:
        raise ValueError("User must have login")

