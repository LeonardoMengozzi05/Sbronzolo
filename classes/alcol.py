from gpiozero import OutputDevice, Button, LED
from classes.loggingConfig import logAlcol
import json
import time
import os 

mock = os.getenv("DEBUG") == "true"
COCKTAIL_FILE = 'jsons/cocktails.json'
ALCOLS_FILE = 'jsons/alcols.json'
MAX = 1000
MIN = 50

class Alcol():
    def __setCocktail(self, disponibility):
        with open(COCKTAIL_FILE, "r", encoding="utf-8") as file:
            cocktails = json.load(file)
        for cocktail in cocktails:
            ing = next(
                (ing for ing in cocktail["ingredienti"] if ing['nome'] == self.alcol),
                None
            )
            if ing:
                ing['disponibilita'] = disponibility
        with open(COCKTAIL_FILE, "w", encoding="utf-8") as file:
            json.dump(cocktails, file, indent=4)

    def __resetAmount(self):
        self.led.off()
        self.amount = MAX
        self.__setCocktail(True)

    def __checkAmount(self):
        if self.amount < MIN:
            self.led.on()
            self.__setCocktail(False)

    def __init__(self, alcol):
        self.alcol = alcol['nome']
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
        logAlcol(f"dispensed {ml}ml of {self.alcol}")
        if not mock: 
            self.pompa.on()
            t = ml / 90 * 60
            time.sleep(t)
            self.pompa.off()
            self.amount -= ml
            self.__checkAmount()

class Alcols():
    def __init__(self):
        with open(ALCOLS_FILE, 'r', encoding='utf-8') as file:
            ALCOLS_DATA = json.load(file)
        self.alcols = [Alcol(alcol) for alcol in ALCOLS_DATA]

    def getAlcolByName(self, alcolName):
        return next((a for a in self.alcols if a.alcol == alcolName), None)

    def stopAll(self):
        for alcol in self.alcols: 
            alcol.pompa.off()
