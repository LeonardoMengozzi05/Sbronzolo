from datetime import datetime 
import asyncio
import threading

timeout = 120

class Client:
    def __init__(self, token, position):
        self.token = token
        self.event = asyncio.Event()
        self.position = position
        self.last_seen = datetime.now() 
    def isLogged(self):
        return (datetime.now() - self.last_seen).seconds < timeout
    def update_activity(self):
        self.last_seen = datetime.now()

class Clients:
    def __init__(self):
        self.clients = []
        self.lock = threading.Lock()

    def add(self, token):
        c = Client(token, len(self.clients))
        with self.lock:
            self.clients.append(c)
        return c

    def isFirst(self, client):
        with self.lock:
            return client.token == self.clients[0].token

    def get(self, token):
        if token is None:
            return None
        with self.lock:
            return next((c for c in self.clients if c.token == token), None)

    def removeSlogged(self):
        def remove(index=0):
            c = self.clients.pop(index)
            for position, client in enumerate(self.clients, index):
                client.position = position
            return c
        with self.lock:
            if len(self.clients) > 0:
                for i in range(len(self.clients) - 1, -1, -1):
                    if not self.clients[i].isLogged():
                        c = remove(i)
                        if i == 0:
                            c.event.set()

    def logout(self):
        with self.lock:
            c = self.clients.remove(0)
            if c is not None:
                c.event.set()
