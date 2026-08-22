from gpiozero import OutputDevice, Button, LED
import json
import time

COCKTAIL_FILE = 'cocktails.json'
ALCOLS_FILE = 'alcols.json'
MAX = 2000
MIN = 50

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
        if self.amount < MIN:
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

class Alcols():
    def __init__(self):
        with open(ALCOLS_FILE, 'r', encoding='utf-8') as file:
            ALCOLS_DATA = json.load(file)
        self.alcols = [Alcol(alcol) for alcol in ALCOLS_FILE]

    def getAlcolByName(self, alcolName):
        return next((a for a in self.alcols if a.alcol == alcolName), None)