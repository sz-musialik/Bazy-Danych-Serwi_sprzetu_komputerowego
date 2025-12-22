# Serwis sprzętu komputerowego - backend

## Instrukcja uruchomienia i testów lokalnych.

### Wymagania:
- Python 3.11 wraz z bibliotekami zdefiniowanymi w pliku `requirements.txt`,
- MySQL.

### Instalacja:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Konfiguracja:
Należy zaktualizować `backend/database.py` aby wskazywał na bazę MySQL (DATABASE_URL).

### Uruchomienie projektu:

1. Uruchomienie środowiska wirutalnego (venv).
2. Uruchomienie serwera MySQL.
3. Wywołanie pliku `debug_tables.py`.
4. Wywołanie pliku `app.py`.

### Testy:
W celu uruchomienia podstawowych testów należy wywołać:

```powershell
pytest -q
```
