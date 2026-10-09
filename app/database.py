from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.inspector import query_store

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    query_store.before_execute(conn, cursor, statement, parameters, context, executemany)

@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    query_store.after_execute(conn, cursor, statement, parameters, context, executemany)
