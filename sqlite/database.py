from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from sqlalchemy import event

SQLALCHEMY_DATABASE_URL = "sqlite:///sqlite.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

event.listen(
    engine, "connect", lambda c, _: c.execute("pragma foreign_keys=on")
)


class Base(DeclarativeBase):
    pass


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
