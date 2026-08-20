from gpiozero import OutputDevice, Button, LED
from multiprocessing.connection import Listener
import json
import time

COCKTAIL_FILE = 'cocktails.json'
ALCOLS_FILE = 'alcols.json'
MAX = 2000
MIN = 200

class Alcol():
    def __setCocktail(self, disponibility):
        with open(COCKTAIL_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        for cocktail in data:
            if any(ing["nome"] == self.alcol for ing in cocktail["ingredienti"]):
                cocktail['disponibilita'] = disponibility
        with open(COCKTAIL_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def __resetAmount(self):
        self.led.off()
        self.amount = MAX
        self.__setCocktail(True)

    def __checkAmount(self):
        if self.amount <= MIN:
            self.led.on()
            self.__setCocktail(False)

    def __init__(self, alcol):
        self.alcol = alcol['alcol']
        self.pompa = OutputDevice(
            alcol['pompa'], 
            active_high=True, 
            initial_value=False
        )
        self.button = Button(alcol['bottone'])
        self.button.when_pressed = self.__resetAmount
        self.led = LED(alcol['led'])
        self.amount = MAX
    
    def dispense(self, ml):
        self.pompa.on()
        t = ml# TODO: formula che converte i ml della ricetta in un tempo congruo alla capacità della pompa
        time.sleep(t)
        self.pompa.off()
        self.amount -= ml
        self.__checkAmount()

def mixing(cocktail):
    for alcol in cocktail["ingredienti"]:
        a = [l for l in alcols if l.alcol == alcol['nome']][0].dispense(cocktail['quantita'])
        time.sleep(0.001)

def loop():
    while True:
        conn = listener.accept()
        mixing(conn.recv().get('cocktail'))
        conn.close()

if __name__ == "__main":
    try:
        ADDRESS = ('0.0.0.0', 6000)
        AUTH_KEY = b'''
            Beh, Shinji, io non posso fare altro che stare qui ad annaffiare. Pero', 
            quanto a te, quanto a quel che non puoi far che tu, per te qualcosa da 
            poter far dovrebbe esserci. Ma non ti costringera' nessuno, pensa da te 
            stesso, decidi da te stesso che cosa tu stesso possa fare. Beh, che tu 
            non abbia rammarichi.
        '''
        listener = Listener(ADDRESS, family='AF_INET', authkey=AUTH_KEY)
        with open(ALCOLS_FILE, 'r', encoding='utf-8') as file:
            ALCOLS_DATA = json.load(file)
        alcols = [Alcol(alcol) for alcol in ALCOLS_FILE]
        loop()
    finally:
        listener.close()