import multiprocessing
from os import environ
from sys import argv

from dotenv import load_dotenv
from discord import Intents

from Jester import LogClient
from Jester import CommandClient

load_dotenv('.env')

class InvalidClientType(Exception):
    def __init__(self):
        self.message = 'ClientType was Invalid!'
        super().__init__(self.message)

class Controller:
    def __init__(self):
        self._intents = Intents.all()
        self._kwargsBot = {
            'token': environ['DISCORD_TOKEN']
        }
        self._validClients = [
            'LogClient'
            ,'CommandClient'
        ]

        try:
            self._clientType = argv[1]
            if self._clientType not in self._validClients:
                print('ClientType was not in valid list. Valid ClientTypes are:')
                for i in self._validClients:
                    print(i)
                raise InvalidClientType()
            else:
                print(f'Using ClientType {self._clientType}...')
        except IndexError as e:
            print("No ClientType entered, using default LogClient...")
            self._clientType = None

        if self._clientType == 'LogClient' or self._clientType is None:
            self.Client = LogClient(command_prefix='!', intents=self._intents)
        elif self._clientType == 'CommandClient':
            self.Client = CommandClient(command_prefix='!', intents=self._intents)

    def start(self):
        self.Client.run(self._kwargsBot['token'])

if __name__ == '__main__':
        app = Controller()
        app.start()