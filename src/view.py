from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Union, List


@dataclass
class Operation:
    command: str
    params: Dict = field(default_factory=dict)

    def as_json(self):
        return json.dumps(dataclasses.asdict(self))


@dataclass
class Menu:
    names: Dict[Union[int, str], Any] = field(default_factory=dict)
    actions: Dict[Union[int, str], Any] = field(default_factory=dict)


class View:
    main_menu: Menu
    project_menu: Menu
    contract_menu: Menu
    active_menu: Menu
    hidden_actions_menu: Menu

    def __init__(self):
        self.main_menu = self.get_main_menu()
        self.project_menu = self.get_project_menu()
        self.contract_menu = self.get_contract_menu()
        self.hidden_actions_menu = self.get_hidden_actions()

        self.active_menu = self.main_menu

    def get_hidden_actions(self):
        return Menu(
            names={
                'c': 'Показать все договоры',
                'p': 'Показать все проекты',
            },
            actions={
                'c': self.show_contracts,
                'p': self.show_projects,
            }

        )

    def get_main_menu(self):
        return Menu(
            names={
                1: 'Проекты',
                2: 'Договоры',
                3: 'Exit',
            },
            actions={
                1: self.show_project_menu,
                2: self.show_contract_menu,
                3: self.exit,
            })

    def print_menu(self):
        for key, item in self.active_menu.names.items():
            print(key, '--', item)

    def back_to_mainmenu(self):
        self.active_menu = self.main_menu

    # hidden menu
    def show_contracts(self):
        return Operation(command=self.show_contracts.__name__).as_json()

    def show_projects(self):
        return Operation(command=self.show_projects.__name__).as_json()

    # project menu
    def get_project_menu(self):
        return Menu(
            names={
                1: 'Создать проект',
                2: 'Добавить договор',
                3: 'Завершить договор',
                4: 'Вернуться в главное меню'
            },
            actions={
                1: self.create_project,
                2: self.add_contract_to_project,
                3: self.close_contract,
                4: self.back_to_mainmenu,
            })

    def show_project_menu(self):
        self.active_menu = self.project_menu

    def create_project(self):
        return Operation(command=self.create_project.__name__).as_json()

    def select_project(self) -> Optional[int]:
        try:
            id = int(input('Введите номер проекта: '))
            return id
        except ValueError:
            self.show_message('Введен неверный номер')

    def add_contract_to_project(self):
        project_id = self.select_project()
        if project_id is None:
            return

        contract_id = self.select_contract()
        if contract_id is None:
            return

        return Operation(command=self.add_contract_to_project.__name__,
                         params={'project_id': project_id,
                                 'contract_id': contract_id}
                         ).as_json()

    # contract menu
    def get_contract_menu(self):
        return Menu(
            names={
                1: 'Создать договор',
                2: 'Подтвердить договор',
                3: 'Завершить договор',
                4: 'Вернуться в главное меню'
            },
            actions={
                1: self.create_contract,
                2: self.confirm_contract,
                3: self.close_contract,
                4: self.back_to_mainmenu,
            })

    def show_contract_menu(self):
        self.active_menu = self.contract_menu

    def create_contract(self):
        return Operation(command=self.create_contract.__name__).as_json()

    def select_contract(self) -> Optional[int]:
        try:
            id = int(input('Введите номер контракта: '))
            return id
        except ValueError:
            self.show_message('Введен неверный номер')

    def confirm_contract(self) -> Optional[str]:
        try:
            id = int(input('Введите номер договора для подтверждения: '))
            return Operation(command=self.confirm_contract.__name__,
                             params={'id': id}
                             ).as_json()
        except ValueError:
            self.show_message('Введен неверный номер')

    def select_contract_for_project(self, contracts):
        try:
            self.show_message("Доступные договоры:")
            self.show_message(*contracts, sep='\n')
            id = int(input('Введите номер договора для добавления в проект: '))
            return Operation(command=self.select_contract_for_project.__name__,
                             params={'id': id}
                             ).as_json()
        except ValueError:
            self.show_message('Введен неверный номер договора')

    def close_contract(self) -> Optional[str]:
        try:
            id = int(input('Введите номер договора для закрытия: '))
            return Operation(command=self.close_contract.__name__,
                             params={'id': id}
                             ).as_json()
        except ValueError:
            self.show_message('Введен неверный номер')

    # main menu
    def show_menu(self) -> Optional[str]:

        self.print_menu()

        option = None
        try:
            option = input('Выберите действие ("c" и "p" для просмотра списков договоров и проектов): ')
            option = option if option in self.hidden_actions_menu.actions else int(option)
        except ValueError:
            self.show_message('Номер не из списка! Попробуйте еще раз.')

        if action := self.hidden_actions_menu.actions.get(option, None):
            return action()

        if action := self.active_menu.actions.get(option, None):
            return action()

        return action

    def show_message(self, message: [str | List], **kwargs):

        if message:
            if isinstance(message, list):
                print(*message, **kwargs)
            else:
                print(message, **kwargs)

    def exit(self) -> str:
        return Operation(command='exit').as_json()

