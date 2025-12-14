# Ensure backend directory is on sys.path so local imports (services, database) resolve when running `python backend\app.py`
from backend.api.clients import clients_bp
from backend.api.orders import orders_bp


import sys
import os
#sys.path.insert(0, os.path.dirname(__file__))

import backend.database as _db
#sys.modules['database'] = _db

from flask import Flask, jsonify, request
import traceback

app = Flask(__name__)

app.register_blueprint(clients_bp)
app.register_blueprint(orders_bp)

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/parts', methods=['POST'])
def create_part():
    payload = request.json or {}
    name = payload.get('nazwa_czesci')
    quantity = payload.get('ilosc_dostepna', 0)
    if not name:
        return jsonify({'error': 'nazwa_czesci required'}), 400

    try:
        # lazy import: importujemy serwis dopiero przy wywołaniu endpointu
        from services.parts_service import PartsService
        part = PartsService.add_part(name, ilosc_dostepna=quantity)
        return jsonify({'id_czesci': part.id_czesci, 'nazwa_czesci': part.nazwa_czesci}), 201
    except Exception as e:
        tb = traceback.format_exc()
        return jsonify({'error': 'failed to create part', 'details': str(e), 'trace': tb}), 500

@app.route('/clients', methods=['POST'])
def create_client():
    payload = request.json or {}

    try:
        from services.client_service import ClientService

        client_id = ClientService.create_client(
            nazwa=payload.get('nazwa'),
            adres=payload.get('adres'),
            email=payload.get('email'),
            telefon=payload.get('telefon'),
        )

        return jsonify({'id_klienta': client_id}), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    except Exception as e:
        tb = traceback.format_exc()
        return jsonify({
            'error': 'failed to create client',
            'details': str(e),
            'trace': tb
        }), 500

if __name__ == '__main__':
    # Przy starcie serwera opcjonalnie inicjalizujemy DB. Jeśli DISABLE_DB=1 to pomijamy.
    disable_db = os.getenv('DISABLE_DB', '0') in ('1', 'true', 'True')
    if not disable_db:
        try:
            # importujemy DB tylko jeśli rzeczywiście chcemy go użyć
            from database import Base, engine
            Base.metadata.create_all(bind=engine)
        except Exception as e:
            print('Warning: nie udało się utworzyć tabel (sprawdź konfigurację DB lub zgodność SQLAlchemy):', e)
            print('Jeśli chcesz uruchomić serwer bez DB (np. do developmentu frontendu), ustaw DISABLE_DB=1')
    else:
        print('Uruchomiono serwer z DISABLE_DB=1 — połączenie z DB jest pominięte.')

    app.run(debug=True, port=5001)
