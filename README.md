# Serwis - backend

Krótka instrukcja uruchomienia i testów lokalnych.

Wymagania:
- Python 3.11
- MySQL (opcjonalnie dla testów lokalnych; testy integracyjne używają SQLite in-memory)

Instalacja:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Konfiguracja bazy danych:
- Zaktualizuj `backend/database.py` aby wskazywał na Twoją bazę MySQL (DATABASE_URL).

Uruchomienie projektu (developer):
- Ten projekt to warstwa backendu przygotowana pod przyszły frontend desktopowy.
- Możesz użyć REPL lub napisać prosty skrypt, aby wywołać serwisy w `backend/services/`.

Testy:

```powershell
pytest -q
```

Uwaga:
- Testy transakcyjne używają SQLite in-memory w celu szybkiego sprawdzenia rollbacków.
- W produkcji używaj MySQL (mysql-connector-python) i uruchom migracje schematu (alembic można dodać jako rozszerzenie).
