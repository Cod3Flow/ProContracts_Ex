from enum import IntEnum
from datetime import date

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, select, update, delete, insert
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now

from dbconnection import DBConnection


class Base(DeclarativeBase):
    pass


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    date_created = Column(DateTime, default=now)
    contracts = relationship("Contract", backref="projects")

    def __init__(self, name: str, date_created: date):
        super().__init__()
        self.name = name
        self.date_created = date_created

    def __repr__(self):
        return f'Проект №{self.id}: {self.name} от {self.date_created}.\n Договоры: {self.contracts}'


class ContractStatus(IntEnum):
    DRAFT = 1
    ACTIVE = 2
    CLOSED = 3


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    date_created = Column(DateTime, default=now)
    date_signed = Column(DateTime)
    status = Column(Integer, default=ContractStatus.DRAFT)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)

    def __init__(self, name: str, date_created: date):
        super().__init__()
        self.name = name
        self.date_created = date_created

    def __repr__(self):
        return f'Договор №{self.id}: {self.name} от {self.date_created}, статус: {self.status}, ' \
               f'подписан: {self.date_signed}, проект №{self.project_id}'

    def is_signed(self):
        return self.date_signed is None


class Model:
    dbc: DBConnection

    def __init__(self):
        self.dbc = DBConnection()
        self.dbc.connect()
        Base.metadata.create_all(bind=self.dbc.engine)

    # CREATE
    def create_item(self, item):
        self.dbc.session.add(item)
        self.commit()
        # TODO: add return

    # READ
    def read_item(self, entity, **ident):
        result = self.dbc.session.get(entity, ident)
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

        return self.dbc.session.scalars(stmt).all()

    # UPDATE
    def update_item(self, entity, id: int, **values):
        stmt = (update(entity)
                .where(entity.id == id)
                .values(**values)
                )
        self.dbc.session.execute(stmt)
        self.commit()
        # TODO: add return

    # DELETE
    def delete_item(self, entity, id: int):
        stmt = delete(entity).where(entity.id == id)
        self.dbc.session.execute(stmt)
        self.commit()

    def delete_all(self, entity):
        self.dbc.session.query(entity).delete()
        self.commit()

    def commit(self):
        self.dbc.session.commit()



