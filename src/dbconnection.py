from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from constants import DEFAULT_DB


class DBConnection:
    engine: Engine
    session: Session

    def __init__(self, db_engine=DEFAULT_DB):
        self.engine = create_engine(db_engine)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def connect(self):
        session = sessionmaker(bind=self.engine)
        self.session = session()

    def disconnect(self):
        self.session.close()


