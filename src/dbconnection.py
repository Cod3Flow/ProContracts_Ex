from sqlalchemy import Engine, create_engine, select, update, delete
from sqlalchemy.orm import Session, sessionmaker

from constants import DEFAULT_DB


class DBQuery:
    session: Session

    def __init__(self, session: Session):
        self.session = session

    # CREATE
    def create_item(self, item):
        self.session.add(item)
        self.commit()
        # TODO: add return

    # READ
    def read_item(self, entity, **ident):
        result = self.session.get(entity, ident)
        return result

    def read_items(self, entity, filter=None):

        if filter is None:
            stmt = (select(entity)
                    .order_by(entity.id)
                    )
        else:
            stmt = (select(entity)
                    .where(filter)
                    .order_by(entity.id)
                    )

        return self.session.scalars(stmt).all()

    # UPDATE
    def update_item(self, entity, id: int, **values):
        stmt = (update(entity)
                .where(entity.id == id)
                .values(**values)
                )
        self.session.execute(stmt)
        self.commit()
        # TODO: add return

    # DELETE
    def delete_item(self, entity, id: int):
        stmt = delete(entity).where(entity.id == id)
        self.session.execute(stmt)
        self.commit()

    def delete_all(self, entity):
        self.session.query(entity).delete()
        self.commit()

    def commit(self):
        self.session.commit()

    def truncate_table(self, entity):
        self.delete_all(entity)


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
