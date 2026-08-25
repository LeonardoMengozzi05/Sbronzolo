from gpiozero import OutputDevice, Button, LED
from gpiozero.pins.mock import MockFactory
from classes.loggingConfig import logAlcol
import gpiozero
import json
import time
import os 

COCKTAIL_FILE = 'data/jsons/cocktails.json'
ALCOLS_FILE = 'data/jsons/alcols.json'
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
                cocktail['disponibile'] = disponibility
        with open(COCKTAIL_FILE, "w", encoding="utf-8") as file:
            json.dump(cocktails, file, indent=4)

    def __resetAmount(self):
        if self.led.is_active:
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
        if os.getenv("DEBUG") == "false": 
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

if __name__ == "__main__":
    os.environ['DEBUG'] = "false"
    MAX = 60
    gpiozero.Device.pin_factory = MockFactory()
    controller = Alcol({
        "nome": "Gin",
        "pompa": 1,
        "bottone": 2,
        "led": 3
    })
    controller.dispense(11)
    assert controller.led.is_active, "Errore: Il LED dovrebbe essere accesso dopo il superamento della soglia minimina."
    with open(COCKTAIL_FILE, "r", encoding="utf-8") as file:
        print(json.load(file))
    assert controller.button.pin is not None
    controller.button.pin.drive_low()
    assert not controller.led.is_active and controller.amount == MAX, "Errore il LED dovrebbe essere spento dopo la pressione del bottone."
    print("Tutti i test ✓...")