# Ensure backend directory is on sys.path so local imports (services, database) resolve when running `python backend\app.py`
from backend.api.clients import clients_bp
from backend.api.orders import orders_bp
from backend.api.parts import parts_bp
from backend.api.parts_used import parts_used_bp
from backend.api.parts_orders import parts_orders_bp


import os
#sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify, request
import traceback

app = Flask(__name__)

app.register_blueprint(clients_bp)
app.register_blueprint(orders_bp)
app.register_blueprint(parts_bp)
app.register_blueprint(parts_used_bp)
app.register_blueprint(parts_orders_bp)

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    disable_db = os.getenv('DISABLE_DB', '0') in ('1', 'true', 'True')
    if not disable_db:
        try:
            from database import Base, engine
            Base.metadata.create_all(bind=engine)
        except Exception as e:
            print('Warning: nie udało się utworzyć tabel (sprawdź konfigurację DB lub zgodność SQLAlchemy):', e)
            print('Jeśli chcesz uruchomić serwer bez DB (np. do developmentu frontendu), ustaw DISABLE_DB=1')
    else:
        print('Uruchomiono serwer z DISABLE_DB=1 — połączenie z DB jest pominięte.')

    app.run(debug=True, port=5001)