from model import Model
from view import View
from controller import Controller


class Client:
    def __init__(self):
        self.controller = Controller(Model(), View())

    def launch(self):
        self.controller.run_app()


if __name__ == '__main__':
    client = Client()
    client.launch()





