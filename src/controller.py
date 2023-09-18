import json
import random
from datetime import date
from typing import Optional, Dict

import randomdata
import exceptions as exc
from model import Model, ContractStatus
from view import View


class Controller:

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
        self.model.create_contract(contract)
        self.view.show_message(f'Создан новый случайный договор: {contract}')

    def confirm_contract(self, id: int):
        """
        Changes contract status to ACTIVE
        """

        self.model.update_contract(id, status=ContractStatus.ACTIVE, date_signed=date.today())

        # TODO: check update status
        self.view.show_message(f'Договор №{id} подтвержден')

    def close_contract(self, id: int):
        """
        Changes contract status to CLOSED
        """

        # TODO: check update status
        self.model.update_contract(id, status=ContractStatus.CLOSED)
        self.view.show_message(f'Договор №{id} завершен')

    def show_contracts(self):
        contracts = self.model.read_contracts()
        self.view.show_message(contracts, sep='\n')

    # projects
    def create_new_project(self, **kwargs):
        project = random.choice(randomdata.projects)

        try:
            self.model.create_project(project)
            self.view.show_message(f'Создан новый случайный проект: {project}')

        except exc.ActiveContractsNotPresent as e:
            self.view.show_message(e)

    def add_contract_to_project(self, project_id: int, contract_id: int):

        try:
            self.model.add_contract_to_project(project_id, contract_id)
            self.view.show_message(f'Договор №{contract_id} добавлен в проект №{project_id}')

        except (exc.ContractIsNotActive, exc.ContractDuplicationInProject, exc.ActiveContractAlreadyExistsInProject) as e:
            self.view.show_message(e)

    def show_projects(self):
        projects = self.model.read_projects()
        if projects:
            self.view.show_message(projects, sep='\n')
        else:
            self.view.show_message('Проекты отсутствуют', sep='\n')
