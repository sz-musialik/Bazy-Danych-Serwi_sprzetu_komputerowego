from backend.database import SessionLocal
import contextlib

@contextlib.contextmanager
def transactional_session():

    session = SessionLocal()
    try:
        with session.begin():
            yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()