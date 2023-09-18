from enum import IntEnum
from datetime import date
from operator import and_
from typing import List, Tuple

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, select, update, delete, insert
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now

import exceptions as exc
from dbconnection import DBConnection, DBQuery


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

    # contract operations
    def create_contract(self, contract: Contract):
        return DBQuery(self.dbc.session).create_item(contract)

    def read_contract(self, contract: Contract) -> Contract:
        return self.read_contract_by_id(contract.id)

    def read_contract_by_id(self, id: int) -> Contract:
        return DBQuery(self.dbc.session).read_item(Contract, id=id)

    def read_contracts(self, filter=None):
        return DBQuery(self.dbc.session).read_items(Contract, filter)

    def update_contract(self, id: int, **kwargs):
        DBQuery(self.dbc.session).update_item(Contract, id, **kwargs)

    def delete_contract(self, contract: Contract):
        DBQuery(self.dbc.session).delete_item(contract)

    def get_active_contracts(self, project_id=None):
        return self.read_contracts(filter=and_(Contract.project_id == project_id,
                                               Contract.status == ContractStatus.ACTIVE
                                               )
                                   )

    def confirm_contract(self, id: int, date_signed):
        self.update_contract(id, status=ContractStatus.ACTIVE, date_signed=date_signed)

    def close_contract(self, id: int):
        self.update_contract(id, status=ContractStatus.CLOSED)

    # project operations
    def create_project(self, project: Project):
        new_project = DBQuery(self.dbc.session).create_item(project)
        return new_project

    def read_project(self, project: Project) -> Project:
        return self.read_project_by_id(project.id)

    def read_project_by_id(self, id: int) -> Project:
        return DBQuery(self.dbc.session).read_item(Project, id=id)

    def read_projects(self, filter=None):
        return DBQuery(self.dbc.session).read_items(Project, filter)

    def create_new_project(self, project: Project, **kwargs):

        # only free active contracts allowed
        active_contracts = self.get_active_contracts()
        if not active_contracts:
            raise exc.ActiveContractsNotPresent('Нет свободных подтвержденных договоров! Создание проекта отменено.')

        self.create_project(project)

    def add_contract_to_project(self, project_id: int, contract_id: int):
        project = self.read_project_by_id(project_id)
        contract = self.read_contract_by_id(contract_id)

        if contract.status != ContractStatus.ACTIVE:
            raise exc.ContractIsNotActive('Договор должен быть в статусе Подтвержден. Добавление отменено.')

        if contract in project.contracts:
            raise exc.ContractDuplicationInProject('Договор уже содержится в проекте. Добавление отменено.')

        active_contracts_in_project = [c for c in project.contracts if c.status == ContractStatus.ACTIVE]
        if active_contracts_in_project:
            active_contract = active_contracts_in_project[0]
            raise exc.ActiveContractAlreadyExistsInProject(f'В проекте уже есть активный договор №{active_contract.id}. Добавление отменено.')

        project.contracts.extend([contract])


