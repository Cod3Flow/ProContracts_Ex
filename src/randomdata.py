from datetime import date
from model import Contract, Project

contracts = [
    Contract('На поставку материалов', date.today()),
    Contract('На поставку канцтоваров', date.today()),
    Contract('На поставку техники', date.today()),
    Contract('На установку оборудования', date.today()),
    Contract('На транспортные услуги', date.today()),
]


projects = [
    Project('Проект по модернизации', date.today()),
    Project('Проект по развитию', date.today()),
]