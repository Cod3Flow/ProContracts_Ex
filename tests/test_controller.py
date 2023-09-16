import random

from sqlalchemy import and_

import randomdata
from controller import Controller
from model import Model, ContractStatus, Contract, Project
from view import View


def contracts_check(controller: Controller):

    contracts = controller.read_contracts()
    assert contracts == []

    # add new + read all
    controller.create_new_contract()
    contracts = controller.read_contracts()
    assert len(contracts) == 1

    new_contract = contracts[0]

    # read
    db_contract = controller.read_contract(new_contract)
    assert db_contract == new_contract

    # set Active + read all
    controller.confirm_contract(new_contract.id)
    new_contract = controller.read_contract(new_contract)
    assert new_contract.status == ContractStatus.ACTIVE

    # read draft
    closed_contracts = controller.read_contracts(filter=(Contract.status == ContractStatus.DRAFT))
    assert len(closed_contracts) == 0

    # read active
    active_contracts = controller.read_contracts(filter=(Contract.status == ContractStatus.ACTIVE))
    assert len(active_contracts) == 1
    print(f'{active_contracts=}')

    # add new + read all
    controller.create_contract(random.choice(randomdata.contracts))
    contracts = controller.read_contracts()
    assert len(contracts) == 2
    print(*contracts, sep='\n')


def projects_check(controller):

    projects = controller.read_projects()
    assert projects == []

    # read active contracts
    active_contracts = controller.get_active_contracts()
    assert len(active_contracts) == 1

    # add new + read all
    controller.create_new_project()
    projects = controller.read_projects()
    assert len(projects) == 1

    new_project = projects[0]
    contract = active_contracts[0]

    controller.add_contract_to_project(project_id=new_project.id, contract_id=contract.id)
    projects = controller.read_projects()
    print(*projects, sep='\n')
    assert len(new_project.contracts) == 1

    # dublicate check
    controller.add_contract_to_project(project_id=new_project.id, contract_id=contract.id)
    assert len(new_project.contracts) == 1
    print(*projects, sep='\n')

    # only 1 active contract allowed check
    controller.create_new_contract()
    contracts = controller.read_contracts()
    print(contracts)
    another_new_contract = contracts[-1]

    controller.confirm_contract(another_new_contract.id)
    controller.add_contract_to_project(project_id=new_project.id, contract_id=another_new_contract.id)

    # close active contract in project
    active_contracts = controller.get_active_contracts(project_id=new_project.id)
    assert len(active_contracts) == 1

    active_contract = active_contracts[0]
    controller.close_contract(active_contract.id)

    # add again
    controller.add_contract_to_project(project_id=new_project.id, contract_id=another_new_contract.id)
    print(new_project)
    assert len(new_project.contracts) == 2

    # check in active
    active_contracts = controller.get_active_contracts(project_id=new_project.id)
    assert another_new_contract in active_contracts


def test_controller():
    controller = Controller(Model(), View())

    controller.truncate_table(Contract)
    controller.truncate_table(Project)
    controller.commit_changes()

    contracts_check(controller)
    projects_check(controller)

