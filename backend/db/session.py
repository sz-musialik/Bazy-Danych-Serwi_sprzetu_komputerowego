from backend.database import SessionLocal
import contextlib

@contextlib.contextmanager
def transactional_session():
    """Context manager that yields a SQLAlchemy Session with automatic commit/rollback.
    Use:
        with transactional_session() as session:
            # do db work
    """
    session = SessionLocal()
    try:
        with session.begin():
            yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()