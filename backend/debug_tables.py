import sys
import os

# upewniamy się, że backend/ jest na sys.path
sys.path.insert(0, os.path.dirname(__file__))

# 🔥 TEN SAM ALIAS CO W app.py
import backend.database as _db
sys.modules['database'] = _db

from database import Base, engine
import models   # 🔥 MUSI BYĆ

print("=== MODELE ZAREJESTROWANE W Base.metadata ===")
for table in Base.metadata.tables:
    print(table)

print("=== TWORZENIE TABEL ===")
Base.metadata.create_all(bind=engine)
print("DONE")
