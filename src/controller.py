import json
import random
from datetime import date
from typing import List, Optional, Dict

from sqlalchemy import and_

import randomdata
from model import Project, Contract, Model, ContractStatus
from view import View


class BaseMixin:
    model: Model
    view: View

    def create_item(self, item):
        return self.model.create_item(item)

    def read_item(self, entity, **ident):
        return self.model.read_item(entity, **ident)

    def read_items(self, entity, filter=None):
        return self.model.read_items(entity, filter)

    def update_item(self, item, **values):
        return self.update_item_by_id(type(item), item.id, **values)

    def update_item_by_id(self, entity, id, **values):
        return self.model.update_item(entity, id, **values)

    def delete_item(self, item):
        self.model.delete_item(type(item), item.id)

    def commit_changes(self):
        self.model.commit()

    def truncate_table(self, entity):
        self.model.delete_all(entity)


class ContractMixin(BaseMixin):

    def create_contract(self, contract: Contract) -> bool:
        return self.create_item(contract)

    def read_contract(self, contract: Contract) -> Contract:
        return self.read_contract_by_id(contract.id)

    def read_contract_by_id(self, id: int) -> Contract:
        return self.read_item(Contract, id=id)

    def read_contracts(self, filter=None) -> List[Contract]:
        return self.read_items(Contract, filter)

    def update_contract(self, contract: Contract, **kwargs):
        self.update_item(contract, **kwargs)

    def update_contract_by_id(self, id: int, **kwargs):
        self.update_item_by_id(Contract, id, **kwargs)

    def delete_contract(self, contract: Contract):
        self.delete_item(contract)


class ProjectMixin(BaseMixin):

    def create_project(self, project: Project) -> bool:
        return self.create_item(project)

    def read_project(self, project: Project) -> Project:
        return self.read_project_by_id(project.id)

    def read_project_by_id(self, id: int) -> Project:
        return self.read_item(Project, id=id)

    def read_projects(self, filter=None) -> List[Project]:
        return self.read_items(Project, filter)


class Controller(ProjectMixin, ContractMixin):

    def __init__(self, model: Model, view: View):
        self.model = model
        self.view = view

        self.commands = {
            'create_contract': self.create_new_contract,
            'confirm_contract': self.confirm_contract,
            'close_contract': self.close_contract,
            'show_contracts': self.show_contracts,
            'create_project': self.create_new_project,
            'add_contract_to_project': self.add_contract_to_project,
            'show_projects': self.show_projects,
        }

    def run_app(self):
        while True:
            operation: Optional[str] = self.view.show_menu()

            if operation:
                try:
                    client_operation: Dict = json.loads(operation)
                except:
                    self.view.show_message(f'Ошибка получения операции')
                    continue

                command = client_operation.get('command', None)
                if command == 'exit':
                    self.view.show_message('Программа завершена')
                    break

                try:
                    if action := self.commands.get(command, None):
                        params = client_operation['params']
                        action(**params)

                except Exception as e:
                    self.view.show_message(f'Ошибка выполнения команды {command}: {e}')
                    continue

    # contracts
    def create_new_contract(self):
        contract = random.choice(randomdata.contracts)
        self.create_contract(contract)
        self.view.show_message(f'Создан новый случайный договор: {contract}')

    def confirm_contract(self, id: int):
        """
        Changes contract status to ACTIVE
        """

        self.update_contract_by_id(id, status=ContractStatus.ACTIVE, date_signed=date.today())

        # TODO: check update status
        self.view.show_message(f'Договор №{id} подтвержден')

    def close_contract(self, id: int):
        """
        Changes contract status to CLOSED
        """

        # TODO: check update status
        self.update_contract_by_id(id, status=ContractStatus.CLOSED)
        self.view.show_message(f'Договор №{id} завершен')

    def show_contracts(self):
        contracts = self.read_contracts()
        self.view.show_message(contracts, sep='\n')

    def get_active_contracts(self, project_id=None):
        active_contracts = self.read_contracts(filter=and_(Contract.project_id == project_id,
                                                           Contract.status == ContractStatus.ACTIVE
                                                           )
                                               )
        return active_contracts

    # projects
    def create_new_project(self, **kwargs):

        # only free active contracts allowed
        active_contracts = self.get_active_contracts()

        if not active_contracts:
            self.view.show_message('Нет свободных активных договоров! Создание проекта отменено.', sep='\n')
            return

        project = random.choice(randomdata.projects)
        self.create_project(project)
        self.view.show_message(f'Создан новый случайный проект: {project}')

    def add_contract_to_project(self, project_id: int, contract_id: int):
        project = self.read_project_by_id(project_id)
        contract = self.read_contract_by_id(contract_id)

        if contract in project.contracts:
            self.view.show_message('Договор уже содержится в проекте. Добавление отменено.')
            return

        active_contracts_in_project = [c for c in project.contracts if c.status == ContractStatus.ACTIVE]
        if active_contracts_in_project:
            active_contract = active_contracts_in_project[0]
            self.view.show_message(f'В проекте уже есть активный договор №{active_contract.id}. Добавление отменено.')
            return

        project.contracts.extend([contract])
        self.commit_changes()
        self.view.show_message(f'Договор №{contract_id} добавлен в проект №{project_id}')

    def show_projects(self):
        projects = self.read_projects()
        if projects:
            self.view.show_message(projects, sep='\n')
        else:
            self.view.show_message('Проекты отсутствуют', sep='\n')
