from nicegui.observables import ObservableDict
from datetime import datetime 
from loggingConfig import logClient
import asyncio
import threading

timeout = 10

class Client():
    def __init__(self, token, position):
        self.token = token
        self.event = asyncio.Event()
        self._position = ObservableDict({'value': position})
        self.last_seen = datetime.now() 
    @property
    def position(self):
        return self._position['value']
    @position.setter
    def position(self, value):
        self._position['value'] = value
    def isLogged(self):
        return (datetime.now() - self.last_seen).seconds < timeout
    def update_activity(self):
        self.last_seen = datetime.now()

class Clients:
    def __init__(self):
        self.clients = []
        self.lock = threading.Lock()

    def add(self, token):
        with self.lock:
            c = Client(token, len(self.clients))
            self.clients.append(c)
            logClient(c, "login")
            return c

    def isFirst(self, client):
        with self.lock:
            if not self.clients or client is None:
                return False
            return client.token == self.clients[0].token

    def get(self, token):
        with self.lock:
            if token is None:
                return None
            return next((c for c in self.clients if c.token == token), None)

    def __removeAt(self, index, msg):
        if 0 <= index < len(self.clients):
            removedClient = self.clients.pop(index)
            logClient(removedClient, msg)
            for position in range(index, len(self.clients)):
                self.clients[position].position = position
                logClient(self.clients[position], f"update position to {position}")
            return True
        return False

    def __startNext(self, firstRemoved):
        if firstRemoved and self.clients:
            self.clients[0].event.set()

    def removeSlogged(self):
        with self.lock:
            if not self.clients:
                return
            firstRemoved = False
            for i in range(len(self.clients) - 1, -1, -1):
                if not self.clients[i].isLogged():
                    if i == 0:
                        firstRemoved = True
                    self.__removeAt(i, "removed")
            self.__startNext(firstRemoved)

    def logout(self):
        with self.lock:
            self.__startNext(self.__removeAt(0, "logout"))
