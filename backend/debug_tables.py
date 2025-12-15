import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import backend.database as _db
sys.modules['database'] = _db

from database import Base, engine

print("=== MODELE ZAREJESTROWANE W Base.metadata ===")
for table in Base.metadata.tables:
    print(table)

print("=== TWORZENIE TABEL ===")
Base.metadata.create_all(bind=engine)
print("DONE")
