import sys
import os
# ensure backend directory and project root are on sys.path so imports resolve
proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
backend_dir = os.path.join(proj_root, 'backend')
# backend_dir first so `import database` resolves to backend/database.py
sys.path.insert(0, backend_dir)
sys.path.insert(0, proj_root)

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend.models.parts import Part
from backend.services.parts_service import PartsService


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:", echo=False, future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    # ensure all model modules are imported so SQLAlchemy can resolve string relationships
    import backend.models.user as _user
    import backend.models.role as _role
    import backend.models.client as _client
    import backend.models.parts as _parts
    import backend.models.parts_used as _parts_used
    import backend.models.order as _order
    import backend.models.order_items as _order_items
    import backend.models.part_orders as _part_orders
    import backend.models.order_parts_status as _order_parts_status
    import backend.models.order_status as _order_status
    import backend.models.equipment_type as _equipment_type
    import backend.models.employee_data as _employee_data

    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_transaction_commit_and_rollback(in_memory_db):
    # tworzenie czesci
    part = PartsService.add_part("Filtr oleju", ilosc_dostepna=10, db=in_memory_db)
    assert part.id_czesci is not None
    assert part.ilosc_dostepna == 10

    # update_stock should commit when using provided session
    updated = PartsService.update_stock(part.id_czesci, -3, db=in_memory_db)
    assert updated.ilosc_dostepna == 7

    # test rollback: spróbuj ustawic ujemny stan i upewnij się, że wyjątek powoduje brak zmian
    with pytest.raises(ValueError):
        PartsService.update_stock(part.id_czesci, -100, db=in_memory_db)

    # after failed operation, stock should remain unchanged
    p = in_memory_db.query(Part).filter(Part.id_czesci == part.id_czesci).first()
    assert p.ilosc_dostepna == 7
