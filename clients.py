from nicegui.observables import ObservableDict
from datetime import datetime 
from loggingConfig import logClient
import asyncio
import threading

timeout = 6

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
        logClient(self, "sono ancora connesso")
        self.last_seen = datetime.now()

class Clients:
    def __init__(self):
        self.clients = []
        self.lock = threading.Lock()

    def add(self, token):
        c = Client(token, len(self.clients))
        with self.lock:
            self.clients.append(c)
            logClient(c, "aggiunto in coda")
        return c

    def isFirst(self, client):
        with self.lock:
            return client.token == self.clients[0].token

    def get(self, token):
        if token is None:
            return None
        with self.lock:
            return next((c for c in self.clients if c.token == token), None)

    def __remove(self, msg, index=0):
        c = self.clients.pop(index)
        logClient(c, msg)
        for position, client in enumerate(self.clients, index):
            client.position = position
            logClient(client, f"Nuova posizione: {position}")
        return c

    def __startNext(self):
        if len(self.clients) > 0:
            self.clients[0].event.set()

    def removeSlogged(self):
        with self.lock:
            if len(self.clients) > 0:
                for i in range(len(self.clients) - 1, -1, -1):
                    if not self.clients[i].isLogged():
                        self.__remove("rimosso per intattività", i)
                        if i == 0:
                            self.__startNext()

    def logout(self):
        with self.lock:
            self.__remove("si è sloggato")
            self.__startNext()
