# Serwis - backend

## Wymagania
- Python 3.11
- MySQL

## Instalacja
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

W przypadku, gdyby baza danych nie zawierała żadnych użytkowników, na których konta można by się zalogować, zostały utworzone pliki `create_admin.py`, `create_employee.py` i `create_manager.py`, które utworzą konta użytkowników o przykładowych danych logowania.

## Konfiguracja bazy danych
Plik `backend/database.py` należy zaktualizować, aby wskazywał na wykorzystywaną bazę MySQL (`DATABASE_URL`).

## Uruchomienie projektu
### Uruchomienie backendu
```bash
.\.venv\Scripts\Activate
python -m backend.debug_tables
python -m backend.app
```

### Uruchomienie frontendu
```bash
.\.venv\Scripts\Activate
python -m frontend.main
```
